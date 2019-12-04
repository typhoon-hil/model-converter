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

psimsch_path = psim_tests_dir + '\\diode.psimsch'


@pytest.fixture(scope='session')
def create_psim_netxml():
    # Generates a xml netlist from psim schematic file
    return psim_export_netxml(psimsch_path)


@pytest.fixture(scope='session')
def convert_xml2tse(create_psim_netxml):
    # Converts the psim xml netlist to tse
    netxml_path = create_psim_netxml
    converter = Converter("psim", netxml_path)
    tse_path = converter.convert_schema(compile_model=False)
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


@pytest.mark.parametrize("Vd1, Vd2, Vd3, f", [(100, 100, 220, 50)])
def test_diode(convert_compile_load, Vd1, Vd2, Vd3, f):

    # Set source value.
    hil.set_source_constant_value(name='Vd1', value=Vd1)
    hil.set_source_constant_value(name='Vd2', value=Vd2)
    hil.set_source_sine_waveform(name='Vd3', rms=Vd3, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['Id1', 'Id2', 'Id3'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Id1 = capture['Id1']
    Id2 = capture['Id2']
    Id3 = capture['Id3']

    # Expected currents
    R = 10
    Id1_exp = Vd1/R
    Id2_exp = 0
    Id3_exp = Vd3/R/np.sqrt(2)

    # Tests
    sig.assert_is_constant(Id1, at_value=around(Id1_exp, tol_p=0.01))
    sig.assert_is_constant(Id2, at_value=around(Id2_exp, tol_p=0.01))
    sig.assert_is_constant(Id3, at_value=around(Id3_exp, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()
