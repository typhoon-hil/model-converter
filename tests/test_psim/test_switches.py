# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\switches\\simple_switches\\switches.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    # ###################################################
    # # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)


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
    Id1 = np.mean(capture['Id1'])
    Id2 = np.mean(capture['Id2'])
    Id3 = np.mean(capture['Id3'])

    # Expected currents
    R = 10
    Id1_exp = Vd1/R
    Id2_exp = 0
    Id3_exp = Vd3/R/np.sqrt(2)

    # Tests
    assert Id1 == pytest.approx(Id1_exp, rel=1e-2)
    assert Id2 == pytest.approx(Id2_exp, abs=0.1)
    assert Id3 == pytest.approx(Id3_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


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
    Imosfet1 = np.mean(capture['Imosfet1'])
    Imosfet2 = np.mean(capture['Imosfet2'])

    # Expected currents
    R = 10
    Imosfet1_exp = Vmosfet1/R
    Imosfet2_exp = Vmosfet2/R/np.sqrt(2)

    # Tests
    assert Imosfet1 == pytest.approx(Imosfet1_exp, rel=1e-2)
    assert Imosfet2 == pytest.approx(Imosfet2_exp, abs=0.2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vigbt1, Vigbt2, f", [(220, 220, 50)])
def test_igbt(convert_compile_load, Vigbt1, Vigbt2, f):

    # Set source value.
    hil.set_source_sine_waveform(name='Vigbt1', rms=Vigbt1, frequency=f)
    hil.set_source_sine_waveform(name='Vigbt2', rms=Vigbt2, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['Iigbt1', 'Iigbt2'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    hil.set_pe_switching_block_control_mode(blockName='IGBT1', switchName='S1', swControl=True)
    hil.set_pe_switching_block_software_value(blockName='IGBT1', switchName='S1', value=1)
    hil.set_pe_switching_block_control_mode(blockName='IGBT2', switchName='S1', swControl=True)
    hil.set_pe_switching_block_software_value(blockName='IGBT2', switchName='S1', value=0)
    capture = get_capture_results(wait_capture=True)
    Iigbt1 = np.mean(capture['Iigbt1'])
    Iigbt2 = np.mean(capture['Iigbt2'])

    # Expected currents
    R = 10
    Iigbt1_exp = Vigbt1/R
    Iigbt2_exp = Vigbt2/R/np.sqrt(2)

    # Tests
    assert Iigbt1 == pytest.approx(Iigbt1_exp, rel=1e-2)
    assert Iigbt2 == pytest.approx(Iigbt2_exp, abs=0.2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vthy, f, thy_value, Ithy_exp",
                         [(220, 50, 1, 15.556),
                          (220, 50, 0, 0)])
def test_thyristor(convert_compile_load, Vthy, f, thy_value, Ithy_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vthy', rms=Vthy, frequency=f)

    # Set switch state
    hil.set_pe_switching_block_control_mode(blockName='THY', switchName='S1', swControl=True)
    hil.set_pe_switching_block_software_value(blockName='THY', switchName='S1', value=thy_value)

    # Start capture
    start_capture(duration=0.1, signals=['Ithy'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Ithy = np.mean(capture['Ithy'])

    # Tests
    assert Ithy == pytest.approx(Ithy_exp, rel=1e-2, abs=0.2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vss, f, ss_value, Iss_exp",
                         [(220, 50, True, 22),
                          (220, 50, False, 0)])
def test_bi_directional_switch(convert_compile_load, Vss, f, ss_value, Iss_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vss', rms=Vss, frequency=f)

    # Set switch state
    hil.set_contactor('SS', swControl=True, swState=ss_value)

    # Start capture
    start_capture(duration=0.1, signals=['Iss'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Iss = np.mean(capture['Iss'])

    # Tests
    assert Iss == pytest.approx(Iss_exp, rel=1e-2, abs=0.2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vss, f, ss_value, Iss_exp",
                         [(220, 50, True, 22),
                          (220, 50, False, 0)])
def test_3ph_bi_directional_switch(convert_compile_load, Vss, f, ss_value, Iss_exp):

    # Set source value
    hil.set_source_sine_waveform(name='V3ph_ss', rms=Vss, frequency=f)

    # Set switch state
    hil.set_contactor('SS', swControl=True, swState=ss_value)

    # Start capture
    start_capture(duration=0.1, signals=['Iss'], executeAt=0.2)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Iss = np.mean(capture['Iss'])

    # Tests
    assert Iss == pytest.approx(Iss_exp, rel=1e-2, abs=0.2)

    # Stop simulation
    hil.stop_simulation()










