# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
from tests.utils import psim_export_netxml
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\single_phase_thyristor_rectifier.psimsch'


@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic file
    return psim_export_netxml(psimsch_path)


@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml[1]
    converter = Converter("psim", netxml_path)
    tse_path = converter.convert_schema(compile_model=False)[0]
    return tse_path


@pytest.fixture(scope='session')
def convert_compile_load(convert_xml2tse):
    tse_path = convert_xml2tse
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)

@pytest.mark.generate_netxml
def test_generate_netxml(create_psim_netxml):
    netxml_path = create_psim_netxml[1]
    assert create_psim_netxml[0] == 0
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert os.path.isfile(tse_path)


@pytest.mark.parametrize("expected_value, ss_state", [(22.0, 1), (0.0, 0)])
def test_thyristor_bridge(convert_compile_load, expected_value, ss_state):

    measurement_name = 'Itb_ac'

    # Set source value.
    start_capture(duration=0.1, signals=[measurement_name], executeAt=1.0)

    # Set switch state
    for i, switch_name in enumerate(['Sa_bot', 'Sa_top', 'Sb_bot', 'Sb_top']):
        hil.set_pe_switching_block_control_mode(blockName='BT1', switchName=switch_name,
                                                swControl=True)
        hil.set_pe_switching_block_software_value(blockName='BT1', switchName=switch_name,
                                                  value=ss_state)
    # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurement = cap_data[measurement_name]

    # Tests:
    sig.assert_is_constant(measurement, at_value=around(expected_value, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()


