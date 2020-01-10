# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
import os
from converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\rlc_branches\\3ph_ac_cable\\3ph_ac_cable.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    # ###################################################
    # # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)


@pytest.mark.parametrize("Vsin3ph, f, theta", [(220, 50, 0)])
def test_ac_cable(convert_compile_load, Vsin3ph, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin3ph', rms=Vsin3ph, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.1, signals=['Iac_cable'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Iac_cable = np.mean(capture['Iac_cable'])

    # Expected currents
    Iac_cable_exp = 42.771

    # Tests
    assert Iac_cable == pytest.approx(Iac_cable_exp, rel=1e-3)

    # Stop simulation
    hil.stop_simulation()









