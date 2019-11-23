# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
import typhoon.test.capture as capture
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import pytest
import os
from model_converter.converter.app.converter import Converter
from tests.utils import psim_export_netxml

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\single_ph_2w_transformer.psimsch'

@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic file
    return psim_export_netxml(psimsch_path)


@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml
    converter = Converter("psim", netxml_path)
    tse_path = converter.convert_schema()
    return tse_path


@pytest.fixture(scope='session')
def compile_tse(convert_xml2tse):
    # Compiles the tse file
    tse_path = convert_xml2tse
    # Convert the model
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd" #
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()

    return cpd_path


@pytest.mark.generate_netxml
def test_generate_netxml(create_psim_netxml):
    netxml_path = create_psim_netxml
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert os.path.isfile(tse_path)


@pytest.mark.compile_only
def test_compile(compile_tse):
    cpd_path = compile_tse
    assert os.path.isfile(cpd_path)


@pytest.mark.parametrize("ss_value, expected, measurement_name",
                         [(False, 219.779, 'Vt_ac'),
                          (True, 874.117, 'It_ac'),
                          (False, 219.779, 'Vti_ac'),
                          (True, 874.117, 'Iti_ac')])
def test_single_ph_2w_transformer(compile_tse, ss_value, expected, measurement_name):
    #Loading model frome funtion 'compile_tse'
    cpd_path = compile_tse
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)
    # Set switch state
    hil.set_contactor('SS1', swControl=True, swState=ss_value)
    hil.set_contactor('SS2', swControl=True, swState=ss_value)

    # Start simulation
    hil.start_simulation()

    capture.start_capture(duration=0.1, signals=[measurement_name], executeAt=1.0)

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)
    measurement = cap_data[measurement_name]

    # Tests
    sig.assert_is_constant(measurement, at_value=around(expected, tol_p=0.001))

    # Stop simulation
    hil.stop_simulation()


