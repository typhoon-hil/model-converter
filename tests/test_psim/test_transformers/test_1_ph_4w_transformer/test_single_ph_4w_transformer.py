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

psimsch_path = psim_tests_dir + '\\single_ph_4w_transformer.psimsch'

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
    tse_path = converter.convert_schema(compile_model=False)[0]
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


@pytest.mark.parametrize("ss5_value, ss6_value, ss7_value, expected_values, measurement_names",
                         [(False, False, False,
                           [219.779, 329.669, 439.559, 0, 0, 0],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (True, False, False,
                           [0, 164.851, 219.802, 874.117, 0, 0],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (False, True, False,
                           [109.901, 0, 219.801,0, 582.745, 0],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (True, True, False,
                           [0, 0, 146.539, 582.764, 388.510, 0],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (False, False, True,
                           [109.901, 164.851, 0, 0, 0, 437.059],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (True, False, True,
                           [0, 109.904, 0, 582.764, 0, 291.383],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (False, True, True,
                           [73.270, 0, 0,0, 388.510, 291.382],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac']),
                          (True, True, True,
                           [0, 0, 0, 437.080, 291.387, 218.541],
                           ['Vt_4w_12_ac', 'Vt_4w_21_ac', 'Vt_4w_22_ac',
                            'It_4w_12_ac', 'It_4w_21_ac', 'It_4w_22_ac'])])
def test_1ph_4w_transformer(compile_tse, ss5_value, ss6_value, ss7_value,
                            expected_values, measurement_names):

    # Loading model frome function 'compile_tse'
    cpd_path = compile_tse
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)

    # Set switch state
    hil.set_contactor('SS5', swControl=True, swState=ss5_value)
    hil.set_contactor('SS6', swControl=True, swState=ss6_value)
    hil.set_contactor('SS7', swControl=True, swState=ss7_value)

    # Set source value.
    hil.set_source_sine_waveform(name='Vt4w', rms=110, frequency=50)

    # Start capture
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)
    measurements = cap_data

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurements[measurement_names[i]], at_value=around(expected_values[i], tol_p=0.001))

    # Stop simulation
    hil.stop_simulation()