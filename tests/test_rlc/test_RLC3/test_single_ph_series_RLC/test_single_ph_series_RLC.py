# Imports
import typhoon.api.hil as hil
from tests.utils import psim_export_netxml
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import pytest
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\test_single_ph_series_RLC.psimsch'


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

@pytest.mark.generate_netxml
def test_generate_netxml(create_psim_netxml):
    netxml_path = create_psim_netxml[1]
    assert create_psim_netxml[0] == 0
    assert os.path.isfile(netxml_path)


@pytest.mark.conversion_xml2tse
def test_conversion_xml2tse(convert_xml2tse):
    tse_path = convert_xml2tse
    assert os.path.isfile(tse_path)











