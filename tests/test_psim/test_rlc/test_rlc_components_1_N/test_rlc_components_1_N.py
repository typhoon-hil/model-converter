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

netlist_path = psim_tests_dir + '\\rlc_components_1_N.xml'


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

# Frequency for all electric circuit
f = 50
# Expected currents:
R3 = 10
L3 = 10e-3
C3 = 100e-6
R31 = 10
IR3_expected = 220 / R3
IL3_expected = 220 / (2*f*np.pi*L3)
IC3R3_expected = 220 / np.sqrt(pow((2*f*np.pi*C3), -2) + pow(R31, 2))
IRL3_expected = 220 / np.sqrt(pow(R3, 2) + pow(L3*2*np.pi*f, 2))
IRC3_expected = 220 / np.sqrt(pow(R3, 2) + pow(C3 * 2 * np.pi * f, -2))
IRLC3_expected = 220 / np.sqrt(pow(R3, 2) + pow(L3 * 2 * np.pi * f - 1 / (C3 * 2 * np.pi * f), 2))

@pytest.mark.parametrize("expected_value, sources_names, measurement_names, ",
                         [(IR3_expected, 'Vsin1', 'IR3'),
                          (IL3_expected, 'Vsin1', 'IL3'),
                          (IC3R3_expected, 'Vsin1', 'IC3R3'),
                          (IRL3_expected, 'Vsin2', "IRL3"),
                          (IRC3_expected, 'Vsin2', 'IRC3'),
                          (IRLC3_expected,'Vsin2', 'IRLC3')])
def test_RLC_current(convert_compile_load, expected_value, sources_names, measurement_names):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin1', rms=220, frequency=50, phase=90)

    # Start capture
    start_capture(duration=0.2, signals=[measurement_names], executeAt=0.5)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    cap_data = get_capture_results(wait_capture=True)
    measured_value= np.mean(cap_data[measurement_names])

    # Tests
    assert measured_value == pytest.approx(expected_value, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()
