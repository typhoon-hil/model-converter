# Imports
import typhoon.api.hil as hil
from tests.utils import psim_export_netxml
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import pytest
import numpy as np
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\synchronous_machine.psimsch'


@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic file
    return psim_export_netxml(psimsch_path)


@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml
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
    netxml_path = create_psim_netxml
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert os.path.isfile(tse_path)


@pytest.mark.parametrize("Vsin_sm, f, Vf, torque, Ism_exp, nr_exp",
                         [(230, 50, 10, 10, 56.64/np.sqrt(2), 1500/60*2*np.pi)])
def test_synchronous_machine(convert_compile_load, Vsin_sm, f, Vf, torque, Ism_exp, nr_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin_sm', rms=Vsin_sm, frequency=f)
    hil.set_source_constant_value(name='Vf', value=Vf)

    # Set machine torque
    hil.set_machine_constant_torque(name='SM', value=torque)

    # Start capture
    start_capture(duration=0.1, signals=['Ism', 'machine mechanical speed'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Ism = capture['Ism']
    nr = capture['machine mechanical speed']

    # Stop simulation
    hil.stop_simulation()

    # Tests
    sig.assert_is_constant(Ism, at_value=around(Ism_exp, tol_p=0.01))
    sig.assert_is_constant(nr, at_value=around(nr_exp, tol_p=0.01))







