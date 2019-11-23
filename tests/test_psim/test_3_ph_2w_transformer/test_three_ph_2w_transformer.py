#IMPORTS
import os
import pytest
import typhoon.api.hil as hil
import numpy as np
import typhoon.test.capture as capture
import typhoon.test.signals as sig
from typhoon.test.ranges import around
from typhoon.api.schematic_editor import model
from model_converter.converter.app.converter import Converter
from tests.utils import psim_export_netxml


vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)
psimsch_path = psim_tests_dir + '\\three_ph_2w_transformer.psimsch'


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
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)

    # Compile the model
    model.compile()

    return cpd_path


@pytest.fixture(scope='session')
def load_cpd(compile_tse):
    cpd_path = compile_tse
    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)
    # Start simulation
    hil.start_simulation()

    yield

    # Stop simulation
    hil.stop_simulation()


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


@pytest.mark.parametrize("Vsin_yy, f, SS_yy, expected_values, measurement_names",
                         [(10000, 50, False,[399.657, 0], ["Vyy", "Iyy"]),
                          (500, 50, True, [0, 352.3], ["Vyy", "Iyy"])])
def test_3ph_yy_transformer(load_cpd, Vsin_yy, f, SS_yy,expected_values, measurement_names):

    # Set source value.
    hil.set_source_sine_waveform(name='Vsin_yy', rms=Vsin_yy/np.sqrt(3), frequency=f)

    # Set switch state
    hil.set_contactor('SS_yy', swControl=True, swState=SS_yy)

    # Start_capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 1.5)

    # Data acquisition
    cap_data=capture.get_capture_results(wait_capture=True)

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(cap_data[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))

@pytest.mark.parametrize("Vsin_dd, f, SS_dd, expected_values, measurement_names",
                         [(10000, 50, False,[399.657, 0], ["Vdd", "Idd"]),
                          (500, 50, True, [0, 1057], ["Vdd", "Idd"])])
def test_3ph_dd_transformer(load_cpd, Vsin_dd, f, SS_dd,expected_values, measurement_names):

    # Set source value.
    hil.set_source_sine_waveform(name='Vsin_dd', rms=Vsin_dd/np.sqrt(3), frequency=f)

    # Set switch state
    hil.set_contactor('SS_dd', swControl=True, swState=SS_dd)

    # Start_capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 1.5)

    # Data acquisition
    cap_data=capture.get_capture_results(wait_capture=True)

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(cap_data[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))
@pytest.mark.parametrize("Vsin_dy, f, SS_dy, expected_values, measurement_names",
                         [(10000, 50, False, [692.227, 0], ['Vdy', 'Idy']),
                          (500, 50, True, [0, 609.840], ['Vdy', 'Idy'])])
def test_3ph_dy_transformer(load_cpd, Vsin_dy, f, SS_dy, expected_values, measurement_names):
    # Set source value.
    hil.set_source_sine_waveform(name='Vsin_dy', rms=Vsin_dy/np.sqrt(3), frequency=f)

    # Set switch state
    hil.set_contactor('SS_dy', swControl=True, swState=SS_dy)

    # Start_capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 1.5)

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(cap_data[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))


@pytest.mark.parametrize("Vsin_yd, f, SS_yd, expected_values, measurement_names",
                         [(10000, 50, False,[230.742, 0], ['Vyd', 'Iyd']),
                          (500, 50, True,[0.0, 610], ['Vyd', 'Iyd'])])
def test_3ph_yd_transformer(load_cpd, Vsin_yd, f, SS_yd, expected_values, measurement_names):

    # Set source value.
    hil.set_source_sine_waveform(name='Vsin_yd', rms=Vsin_yd/np.sqrt(3), frequency=f)

    # Set switch state
    hil.set_contactor('SS_yd', swControl=True, swState=SS_yd)

    # Start_capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 1.5)

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(cap_data[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))
