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

netlist_path = psim_tests_dir + '\\three_phase_thyristor_rectifier.xml'


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


# Constant parameters:
Vtb = V3ph_tb = Vsrc = 220
R = 10
f = 10
# Expected currents:
Itb_ac_exp = Vtb/R
Itb_dc_exp = Vtb/R*2*np.sqrt(2)/np.pi
I3ph_tb_ac_exp = V3ph_tb / R * np.sqrt(2) * 1.654
I3ph_tb_dc_exp = V3ph_tb / R * np.sqrt(2) * 1.655


@pytest.mark.parametrize("expected_values, ss_state, measurement_names, switch_names, block_name, source_name",
                         [([0, 0], 0,
                          ['I3ph_tb_ac', 'I3ph_tb_dc'], ['Sa_top', 'Sb_top', 'Sc_top'], 'BT32', 'V3ph_tb'),
                          ([I3ph_tb_ac_exp, I3ph_tb_dc_exp], 1,
                          ['I3ph_tb_ac', 'I3ph_tb_dc'], ['Sa_bot', 'Sb_bot', 'Sc_bot'], 'BT32', 'V3ph_tb')])
def test_3ph_thyristor_bridge(convert_compile_load, expected_values, ss_state,
                          measurement_names, switch_names, block_name, source_name):

    # Set source value.
    hil.set_source_sine_waveform(name='V3ph_tb', rms=V3ph_tb, frequency=f)
    start_capture(duration=0.1, signals=measurement_names, executeAt=1.0)

    # Set switch state
    for i, switch_name in enumerate(switch_names):
        hil.set_pe_switching_block_control_mode(blockName=block_name, switchName=switch_name,
                                                swControl=True)
        hil.set_pe_switching_block_software_value(blockName=block_name, switchName=switch_name,
                                                  value=ss_state)
    # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurements = cap_data

    # Tests:
    for j, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurements[measurement_names[j]], at_value=around(expected_value, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()

