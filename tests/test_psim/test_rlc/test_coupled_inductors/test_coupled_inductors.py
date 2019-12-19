# Imports
import typhoon.api.hil as hil
import typhoon.test.signals as sig
from typhoon.test.ranges import around
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import os
from model_converter.converter.app.converter import Converter


vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\coupled_inductors.xml'


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

    # Start simulation
    hil.start_simulation()

    yield

    hil.stop_simulation()


@pytest.mark.parametrize("Vsin, expected_values, source_name, measurement_names",
                         [(220, [2.9641208, 0.9154214],
                          'Vsin1', ['I_C2_1', 'I_C2_2']),
                          (220, [21.942844, 10.971465, 0.6202843],
                          'Vsin2', ['I_C3_1', 'I_C3_2', 'I_C3_3']),
                          (220, [21.9239, 14.6160, 9.4619, 0.6405],
                          'Vsin3', ['I_C4_1', 'I_C4_2', 'I_C4_3', 'I_C4_4'])])
def test_coupled_inductors(convert_compile_load, Vsin, expected_values, source_name, measurement_names):

    # Set source value
    hil.set_source_sine_waveform(name=source_name, rms=Vsin, frequency=50, phase=0)

    # Start capture
    sim_time = hil.get_sim_time()
    start_capture(duration=0.1, signals=measurement_names, executeAt=sim_time + 0.5)

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measurement = cap_data

    # Tests
    for i, expected_value in enumerate(expected_values):
        sig.assert_is_constant(measurement[measurement_names[i]], at_value=around(expected_value, tol_p=0.001))
