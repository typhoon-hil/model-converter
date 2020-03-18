# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
import os
from converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\rlc_branches\\rlc_components_1_N\\rlc_components_1_N.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again
    # or if you just change test file, and not xml netlist
    ###################################################
    # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    # ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)


@pytest.mark.parametrize("Vsin1, f, theta", [(220, 50, 90)])
def test_R3(convert_compile_load, Vsin1, f, theta):

    # Expected current
    R3 = 10
    IR3_expected = Vsin1 / R3

    # Set source value
    hil.set_source_sine_waveform(name='Vsin1', rms=Vsin1, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.2, signals=['IR3'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IR3 = np.mean(capture['IR3'])

    # Tests
    assert IR3 == pytest.approx(IR3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin1, f, theta", [(220, 50, 90)])
def test_L3(convert_compile_load, Vsin1, f, theta):

    # Expected current
    L3 = 10e-3
    IL3_expected = Vsin1 / (2*f*np.pi*L3)

    # Set source value
    hil.set_source_sine_waveform(name='Vsin1', rms=Vsin1, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.2, signals=['IL3'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IL3 = np.mean(capture['IL3'])

    # Tests
    assert IL3 == pytest.approx(IL3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin1, f, theta", [(220, 50, 90)])
def test_C3(convert_compile_load, Vsin1, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin1', rms=Vsin1, frequency=f, phase=theta)

    # Expected current
    C3 = 100e-6
    R31 = 10
    IC3R3_expected = Vsin1 / np.sqrt(pow((2*f*np.pi*C3), -2) + pow(R31, 2))

    # Start capture
    start_capture(duration=0.2, signals=['IC3R3'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IC3R3 = np.mean(capture['IC3R3'])

    # Tests
    assert IC3R3 == pytest.approx(IC3R3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin2, f, theta", [(220, 50, 90)])
def test_RL3(convert_compile_load, Vsin2, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin2', rms=220, frequency=f, phase=theta)

    # Expected current
    R3 = 10
    L3 = 10e-3
    IRL3_expected = Vsin2 / np.sqrt(pow(R3, 2) + pow(L3*2*np.pi*f, 2))

    # Start capture
    start_capture(duration=0.2, signals=["IRL3"], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IRL3 = np.mean(capture['IRL3'])

    # Tests
    assert IRL3 == pytest.approx(IRL3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin2, f, theta", [(220, 50, 90)])
def test_RC3(convert_compile_load, Vsin2, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin2', rms=220, frequency=f, phase=theta)

    # Expected current
    R3 = 10
    C3 = 100e-6
    IRC3_expected = Vsin2 / np.sqrt(pow(R3, 2) + pow(C3*2*np.pi*f, -2))

    # Start capture
    start_capture(duration=0.2, signals=["IRC3"], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IRC3 = np.mean(capture['IRC3'])

    # Tests
    assert IRC3 == pytest.approx(IRC3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin2, f, theta", [(220, 50, 90)])
def test_RLC3(convert_compile_load, Vsin2, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin2', rms=220, frequency=f, phase=theta)

    # Expected current
    R3 = 10
    L3 = 10e-3
    C3 = 100e-6
    IRLC3_expected = Vsin2 / np.sqrt(pow(R3, 2) + pow(L3*2*np.pi*f - 1/(C3*2*np.pi*f), 2))

    # Start capture
    start_capture(duration=0.2, signals=["IRLC3"], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    IRLC3 = np.mean(capture['IRLC3'])

    # Tests
    assert IRLC3 == pytest.approx(IRLC3_expected, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()
