# Imports
import typhoon.api.hil as hil
from tests.utils import psim_export_netxml
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import pytest
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\test_capacitor.psimsch'


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

    # Start simulation
    hil.start_simulation()

    yield

    # Stop simulation
    hil.stop_simulation()

@pytest.mark.generate_netxml
def test_generate_netxml(create_psim_netxml):
    netxml_path = create_psim_netxml[1]
    assert create_psim_netxml[0] == 0
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert os.path.isfile(tse_path)


def test_capacitance(convert_compile_load):

    # Start capture
    sim_time = hil.get_sim_time()
    start_capture(duration=0.01, signals=["Vc1"], executeAt=sim_time + 0.5)

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurement = cap_data

    # Tests
    sig.assert_is_constant(measurement["Vc1"], at_value=around(199.0, tol_p=0.001))


def test_cap_init_voltage(convert_compile_load):

    # Start capture
    sim_time = hil.get_sim_time()
    start_capture(duration=0.01, signals=["VP9"], executeAt=sim_time + 0.5)

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurement = cap_data

    # Tests
    sig.assert_is_constant(measurement["VP9"], at_value=around(48.8, tol_p=0.01))











