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

netlist_path = psim_tests_dir + \
               '\\references\\motor_drive_module\\permanent_magnet_sync_machine_v\\permanent_magnet_sync_machine_v.xml'

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
    Ipmsm = np.mean(capture['Ipmsm'])
    nr = np.mean(capture['machine mechanical speed'])

    # Stop simulation
    hil.stop_simulation()

    # Tests
    assert Ipmsm == pytest.approx(expected=Ipmsm_exp, rel=1e-2)
    assert nr == pytest.approx(expected=nr_exp, rel=1e-3)







