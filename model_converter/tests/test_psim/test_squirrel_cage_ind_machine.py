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

netlist_path = psim_tests_dir + \
               '\\references\\motor_drive_module\\squirrel_cage_ind_machine\\squirrel_cage_ind_machine.xml'


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


@pytest.mark.parametrize("Vsin3_sqim, f, torque, Isqim_exp, nr_exp",
                         [(220/np.sqrt(3), 50, 30, 12.866, 988.547/60*2*np.pi)])
def test_squirrel_cage_ind_machine(convert_compile_load, Vsin3_sqim, f, torque, Isqim_exp, nr_exp):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin3_sqim', rms=Vsin3_sqim, frequency=f)

    # Set machine torque
    hil.set_machine_constant_torque(name='SQIM', value=torque)

    # Start capture
    start_capture(duration=0.1, signals=['Isqim', 'machine mechanical speed'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Isqim = np.mean(capture['Isqim'])
    nr = np.mean(capture['machine mechanical speed'])

    # Stop simulation
    hil.stop_simulation()

    # Tests
    assert Isqim == pytest.approx(expected=Isqim_exp, rel=1e-2)
    assert nr == pytest.approx(expected=nr_exp, rel=1e-3)







