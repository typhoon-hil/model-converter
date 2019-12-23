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

psimsch_path = psim_tests_dir + '\\permanent_magnet_sync_machine_v.psimsch'

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


@pytest.mark.parametrize("Vpmsm, f, torque, Ipmsm_exp, nr_exp",
                         [(220/np.sqrt(3), 25, 5, 11.2147, 750/60*2*np.pi)])
def test_permanent_magnet_sync_machine(convert_compile_load, Vpmsm, f, torque, Ipmsm_exp, nr_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vpmsm', rms=Vpmsm, frequency=f)

    # Set machine torque
    hil.set_machine_constant_torque(name='PMSM', value=torque)

    # Start capture
    start_capture(duration=0.1, signals=['Ipmsm', 'machine mechanical speed'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Ipmsm = capture['Ipmsm']
    nr = capture['machine mechanical speed']

    # Stop simulation
    hil.stop_simulation()

    # Tests
    sig.assert_is_constant(Ipmsm, at_value=around(Ipmsm_exp, tol_p=0.02))
    sig.assert_is_constant(nr, at_value=around(nr_exp, tol_p=0.01))







