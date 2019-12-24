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

psimsch_path = psim_tests_dir + '\\single_ph_3w_transformer.psimsch'

#this fixture  will be instanced once per test session
@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic file
    return psim_export_netxml(psimsch_path)


#this fixture  will be instanced once per test session
@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml
    converter = Converter("psim", netxml_path)
    tse_path = converter.convert_schema()[0]
    return tse_path


#this fixture  will be instanced once per test session
@pytest.fixture(scope='session')
def compile_tse(convert_xml2tse):
    # Compiles the tse file
    tse_path = convert_xml2tse
    # Comment this if don't wont to compile model again
    # ###################################################
    # # Convert the model
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


@pytest.mark.parametrize("ss3_value, ss4_value, expected_values, measurement_names",
                         [(False, False, [219.779, 329.669, 0, 0],
                           ['Vt_3w_2_ac', 'Vt_3w_3_ac', 'It_3w_2_ac', 'It_3w_3_ac']),
                          (True, False, [0, 164.851, 874.117, 0],
                           ['Vt_3w_2_ac', 'Vt_3w_3_ac', 'It_3w_2_ac', 'It_3w_3_ac']),
                          (False, True, [109.901, 0, 0, 582.745],
                           ['Vt_3w_2_ac', 'Vt_3w_3_ac', 'It_3w_2_ac', 'It_3w_3_ac']),
                          (True, True, [0, 0, 582.764, 388.510],
                           ['Vt_3w_2_ac', 'Vt_3w_3_ac', 'It_3w_2_ac', 'It_3w_3_ac'])])
def test_single_ph_3w_transformer(compile_tse, ss3_value, ss4_value, expected_values, measurement_names):

    # Loading model frome function 'compile_tse'
    cpd_path = compile_tse
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)

    # Set switch state
    hil.set_contactor('SS3', swControl=True, swState=ss3_value)
    hil.set_contactor('SS4', swControl=True, swState=ss4_value)

    # Set source value.
    hil.set_source_sine_waveform(name='Vt3w', rms=110.0, frequency=50.0)

    # Start capture
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=0.6)

     # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)
    measurements=cap_data

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurements[measurement_names[i]], at_value=around(expected_values[i], tol_p=0.001))

    # Stop simulation
    hil.stop_simulation()
