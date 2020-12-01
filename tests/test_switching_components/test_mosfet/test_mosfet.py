# Imports
import typhoon.api.hil as hil
from tests.utils import psim_export_netxml
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import numpy as np
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\mosfet.psimsch'


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


@pytest.mark.parametrize("Vmosfet1, Vmosfet2, f", [(220, 220, 50)])
def test_mosfet(convert_compile_load, Vmosfet1, Vmosfet2, f):

    # Set source value.
    hil.set_source_sine_waveform(name='Vmosfet1', rms=Vmosfet1, frequency=f)
    hil.set_source_sine_waveform(name='Vmosfet2', rms=Vmosfet2, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['Imosfet1', 'Imosfet2'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    hil.set_pe_switching_block_control_mode(blockName='Q1', switchName='S1', swControl=True)
    hil.set_pe_switching_block_software_value(blockName='Q1', switchName='S1', value=1)
    hil.set_pe_switching_block_control_mode(blockName='Q2', switchName='S1', swControl=True)
    hil.set_pe_switching_block_software_value(blockName='Q2', switchName='S1', value=0)
    capture = get_capture_results(wait_capture=True)
    Imosfet1 = capture['Imosfet1']
    Imosfet2 = capture['Imosfet2']

    # Expected currents
    R = 10
    Imosfet1_exp = Vmosfet1/R
    Imosfet2_exp = Vmosfet2/R/np.sqrt(2)

    # Tests
    sig.assert_is_constant(Imosfet1, at_value=around(Imosfet1_exp, tol_p=0.01))
    sig.assert_is_constant(Imosfet2, at_value=around(Imosfet2_exp, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()
