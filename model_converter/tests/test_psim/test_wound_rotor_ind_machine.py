# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results, wait_capture_finish
import pytest
import numpy as np
import os
from converter.app.converter import Converter


vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\motor_drive_module\\wound_rotor_ind_machine\\wound_rotor_ind_machine.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    ###################################################
    # Convert the model
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


@pytest.mark.parametrize("Vsin3_wrim, f, torque, Iwrim_s_exp, Iwrim_r_exp, nr_exp",
                         [(220, 50, 5, 3.1929/np.sqrt(2), 1.9932/np.sqrt(2), 1361)])
def test_wound_rotor_ind_machine(convert_compile_load, Vsin3_wrim, f, torque, Iwrim_s_exp, Iwrim_r_exp, nr_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin3_wrim', rms=Vsin3_wrim, frequency=f)

    # Set machine torque
    hil.set_machine_constant_torque(name='WRIM', value=torque)

    # Start capture
    start_capture(duration=2.5, rate=10000, signals=['Iwrim_s', 'Iwrim_r', 'machine mechanical speed'], executeAt=0.5)

    # Start simulation
    hil.start_simulation()
    wait_capture_finish()

    # Data acquisition
    capture = get_capture_results()
    Iwrim_s = np.mean(capture['Iwrim_s'])
    #Iwrim_r = np.mean(util.window_rms(capture['Iwrim_r'].values, window_size=5000))
    nr = np.mean(capture['machine mechanical speed'])/2/np.pi*60

    # Stop simulation
    hil.stop_simulation()

    # Tests
    assert Iwrim_s == pytest.approx(expected=Iwrim_s_exp, rel=1e-2)
    #assert Iwrim_r == pytest.approx(expected=Iwrim_r_exp, rel=1e-2)
    assert nr == pytest.approx(expected=nr_exp, rel=1e-3)










