# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
import typhoon.test.capture as capture
import pytest
import os
from converter.app.converter import Converter
from tests.utils import psim_export_netxml

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

psimsch_path = psim_tests_dir + '\\ideal_transformer.psimsch'


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
def compile_tse(convert_xml2tse):
    # Compiles th tse file
    tse_path = convert_xml2tse
    # Comment this if don't wont to compile model again
    # ###################################################
    # # Convert the model
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()

    return cpd_path


@pytest.fixture(scope='session')
def load_simulate(compile_tse):
    # Load to VHIL
    cpd_path = compile_tse
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)
    # Set source value.
    hil.set_source_sine_waveform(name='Vit', rms=110, frequency=50)
    hil.set_source_sine_waveform(name='Viti1', rms=220, frequency=50)

    # Start capture
    capture.start_capture(duration=0.1, signals=['Vit_ac', 'Viti_ac'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    yield capture.get_capture_results(wait_capture=True)

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


def test_ideal_transformer(load_simulate):
    cap_data = load_simulate
    # Data acquisition
    Vit_ac = cap_data['Vit_ac']
    Vit_ac_rms = Vit_ac.mean()

    # Tests
    assert Vit_ac_rms == pytest.approx(220, rel=1e-3)


def test_ideal_transformer_inverted(load_simulate):
    cap_data = load_simulate
    # Data acquisition
    Viti_ac = cap_data['Viti_ac']
    Viti_ac_rms = Viti_ac.mean()

    # Test
    assert Viti_ac_rms == pytest.approx(440, rel=1e-3)





