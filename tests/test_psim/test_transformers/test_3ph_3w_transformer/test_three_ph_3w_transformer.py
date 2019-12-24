# IMPORTS
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


# Define paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)
psimsch_path = psim_tests_dir + '\\three_ph_3w_transformer.psimsch'


@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic files
    return psim_export_netxml(psimsch_path)


@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml[1]
    converter = Converter("psim", netxml_path)
    tse_path = converter.convert_schema()[0]
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

    # Set source value
    hil.set_source_sine_waveform(name='Vsin_ydd', rms=1000 / np.sqrt(3), frequency=50)
    hil.set_source_sine_waveform(name='Vsin_yyd', rms=1000 / np.sqrt(3), frequency=50)

    # Start simulation
    hil.start_simulation()

    yield

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.generate_netxml
def test_generate_xml(create_psim_netxml):
    netxml_path = create_psim_netxml[1]
    assert create_psim_netxml[0] == 0
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert  os.path.isfile(tse_path)


@pytest.mark.compile_only
def test_compile(compile_tse):
    cpd_path = compile_tse
    assert os.path.isfile(cpd_path)

@pytest.mark.parametrize("contactor_state1, contactor_state2, expected_values, contactor_name1, contactor_name2, measurement_names",
                         [(False, False, [432.661, 288.441, 0, 0],
                          'ss_ydd2', 'ss_ydd3', ['Vydd2', 'Vydd3', 'Iydd2', 'Iydd3']),
                          (False, True, [299.350, 0, 0, 143.507],
                           'ss_ydd2', 'ss_ydd3', ['Vydd2', 'Vydd3', 'Iydd2', 'Iydd3']),
                          (True, False, [0, 171.067, 113.480, 0],
                           'ss_ydd2', 'ss_ydd3', ['Vydd2', 'Vydd3', 'Iydd2', 'Iydd3']),
                          (True, True, [0, 0, 88.431, 95.859],
                           'ss_ydd2', 'ss_ydd3', ['Vydd2', 'Vydd3', 'Iydd2', 'Iydd3']),
                          (False, False, [749.391, 288.441, 0, 0],
                           'ss_yyd2', 'ss_yyd3', ['Vyyd2', 'Vyyd3', 'Iyyd2', 'Iyyd3']),
                          (False, True, [518.490, 0, 0, 143.507],
                           'ss_yyd2', 'ss_yyd3', ['Vyyd2', 'Vyyd3', 'Iyyd2', 'Iyyd3']),
                          (True, False, [0, 171.067, 65.518, 0],
                           'ss_yyd2', 'ss_yyd3', ['Vyyd2', 'Vyyd3', 'Iyyd2', 'Iyyd3']),
                          (True, True, [0, 0, 51.056, 95.859],
                           'ss_yyd2', 'ss_yyd3', ['Vyyd2', 'Vyyd3', 'Iyyd2', 'Iyyd3'])])

def test_three_ph_3w_ydd_transformer(load_cpd, contactor_state1, contactor_state2, expected_values, contactor_name1, contactor_name2, measurement_names):

    # Set switch state
    hil.set_contactor(contactor_name1, swControl=True, swState=contactor_state1)
    hil.set_contactor(contactor_name2, swControl=True, swState=contactor_state2)

    # Start capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 1.5)

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)
    measurements=cap_data

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurements[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))

