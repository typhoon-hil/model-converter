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


@pytest.mark.parametrize("source_value, contactor_state, expected_value, source_name, contactor_name, measurement_name",
                          [(10000, False,  399.657,
                           'Vsin_yy', 'SS_yy', "Vyy"),
                            (500, True, 352.3,
                           'Vsin_yy', 'SS_yy', "Iyy"),
                            (10000, False, 399.657,
                           'Vsin_dd', 'SS_dd', "Vdd"),
                            (500, True,  1057,
                           'Vsin_dd', 'SS_dd', "Idd"),
                            (1000, False,  692.227,
                           'Vsin_dy', 'SS_dy', "Vdy"),
                            (500, True, 609.840,
                           'Vsin_dy', 'SS_dy', "Idy"),
                            (10000, False, 230.742,
                           'Vsin_yd', 'SS_yd', "Vyd"),
                            (500, True, 610,
                           'Vsin_yd', 'SS_yd', "Iyd")])
def test_3ph_w1w2_transformer(load_cpd, source_value, contactor_state, expected_value, source_name, contactor_name,  measurement_name):

    # Set source value.
    hil.set_source_sine_waveform(name=source_name, rms=source_value/np.sqrt(3), frequency=50)

    # Set switch state
    hil.set_contactor(name=contactor_name, swControl=True, swState=contactor_state)

    # Start_capture
    sim_time = hil.get_sim_time()
    capture.start_capture(duration=0.1, signals=[measurement_name], executeAt=sim_time + 2)

    # Data acquisition
    cap_data = capture.get_capture_results(wait_capture=True)
    measurement = cap_data[measurement_name]

    # Tests
    sig.assert_is_constant(measurement, at_value=around(expected_value, tol_p=0.001))