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

netlist_path = psim_tests_dir + '\\references\\rlc_branches\\coupled_inductors\\coupled_inductors.xml'


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


@pytest.mark.parametrize("Vsin1, f, theta", [(220, 50, 0)])
def test_coupled_inductors2(convert_compile_load, Vsin1, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin1', rms=Vsin1, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.1, signals=['I_C2_1', 'I_C2_2'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    I_C2_1 = np.mean(capture['I_C2_1'])
    I_C2_2 = np.mean(capture['I_C2_2'])

    # Expected currents
    I_C2_1_exp = 2.9641208
    I_C2_2_exp = 0.9154214

    # Tests
    assert I_C2_1 == pytest.approx(I_C2_1_exp, rel=1e-2)
    assert I_C2_2 == pytest.approx(I_C2_2_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin2, f, theta", [(220, 50, 0)])
def test_coupled_inductors3(convert_compile_load, Vsin2, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin2', rms=Vsin2, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.1, signals=['I_C3_1', 'I_C3_2', 'I_C3_3'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    I_C3_1 = np.mean(capture['I_C3_1'])
    I_C3_2 = np.mean(capture['I_C3_2'])
    I_C3_3 = np.mean(capture['I_C3_3'])

    # Expected currents
    I_C3_1_exp = 21.942844
    I_C3_2_exp = 10.971465
    I_C3_3_exp = 0.6202843

    # Tests
    assert I_C3_1 == pytest.approx(I_C3_1_exp, rel=1e-2)
    assert I_C3_2 == pytest.approx(I_C3_2_exp, rel=1e-2)
    assert I_C3_3 == pytest.approx(I_C3_3_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vsin3, f, theta", [(220, 50, 0)])
def test_coupled_inductors4(convert_compile_load, Vsin3, f, theta):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin3', rms=Vsin3, frequency=f, phase=theta)

    # Start capture
    start_capture(duration=0.1, signals=['I_C4_1', 'I_C4_2', 'I_C4_3', 'I_C4_4'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    I_C4_1 = np.mean(capture['I_C4_1'])
    I_C4_2 = np.mean(capture['I_C4_2'])
    I_C4_3 = np.mean(capture['I_C4_3'])
    I_C4_4 = np.mean(capture['I_C4_4'])

    # Expected currents
    I_C4_1_exp = 21.9239
    I_C4_2_exp = 14.6160
    I_C4_3_exp = 9.4619
    I_C4_4_exp = 0.6405

    # Tests
    assert I_C4_1 == pytest.approx(I_C4_1_exp, rel=1e-2)
    assert I_C4_2 == pytest.approx(I_C4_2_exp, rel=1e-2)
    assert I_C4_3 == pytest.approx(I_C4_3_exp, rel=1e-2)
    assert I_C4_4 == pytest.approx(I_C4_4_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()






