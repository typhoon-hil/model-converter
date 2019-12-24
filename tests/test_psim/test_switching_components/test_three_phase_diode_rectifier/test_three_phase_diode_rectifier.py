# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\three_phase_diode_rectifier.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    # ###################################################
    # # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)[0]
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)

# Constant parameters
Vdb = V3ph_db = Vsrc = 220
R = 10.0
f = 50
# Expected currents
Idb_ac_exp = Vdb/R
Idb_dc_exp = Vdb/R*2*np.sqrt(2)/np.pi
I3ph_db_ac_exp = V3ph_db / R * np.sqrt(2) * 1.654
I3ph_db_dc_exp = V3ph_db / R * np.sqrt(2) * 1.655
@pytest.mark.parametrize("expected_values, measurement_names, source_name",
                         [([I3ph_db_ac_exp, I3ph_db_dc_exp], ['I3ph_db_ac', 'I3ph_db_dc'], 'V3ph_db')])
def test_rectifiers(convert_compile_load, expected_values, measurement_names, source_name):

    # Set source value.
    hil.set_source_sine_waveform(name=source_name, rms=Vsrc, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=measurement_names, executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurements = cap_data

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurements[measurement_names[i]], at_value=around(expected_value, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()