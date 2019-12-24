# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
import typhoon.test.capture as capture
from typhoon.test.ranges import around
import pytest
import numpy as np
import pandas as pd
import os
import logging
from model_converter.converter.app.converter import Converter
import typhoon.test.signals as sig
logger = logging.getLogger(__name__)

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\rlc_components_1_1.xml'
capture_time = 0.01


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    # ###################################################
    # # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)[0]
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)



@pytest.mark.parametrize("VDC, Vin, Vout, I", [
                        (100.0, 100.0, 80.0, 2.0),])
def test_resistor_divider(convert_compile_load, VDC, Vin, Vout, I):
    # Start simulation
    hil.start_simulation()

    # Set source value
    hil.set_source_constant_value(name='VDC', value=VDC)
    hil.wait_msec(1.0)


    # Tests
    assert capture.read('VDC') == VDC
    assert capture.read('Vin') == Vin
    assert capture.read('Vout') == Vout
    assert capture.read('I') == I

    # Stop simulation
    hil.stop_simulation()



@pytest.mark.parametrize("VDC1, L1, IL1_0",
                         [(100, 10e-3, 50)])
def test_inductor_dc(convert_compile_load, VDC1, L1, IL1_0):

    # Set sources before starting the simulation
    hil.set_source_constant_value(name='VDC1', value=VDC1)

    # Start capture
    channel_list = ["IL1"]

    # Expected current
    IL1_expected = VDC1 * capture_time / L1 + IL1_0

    capture.start_capture(duration=capture_time, rate=1000, signals=channel_list, trigger_source="Forced",
                          trigger_use_first_occurence=True, fileName="")

    # Start simulation
    hil.start_simulation()

    # Wait capture to finish()
    capture.wait_capture_finish()

    # Evaluate capture results
    cap_data = capture.get_capture_results()
    measurements = cap_data["IL1"]

    # Calculate the measured current after one second
    IL1_measured = measurements[-1]

    # Check if captured current ise the ramp with the last value equal to the I_l_expected
    slope = VDC1 / L1  # slope of the linear voltage growth
    tolerance=0.01*IL1_expected
    sig.assert_is_ramp(measurements, slope=slope, tol=tolerance)
    assert IL1_measured == pytest.approx(IL1_expected, abs=tolerance)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.convert_compile_load
def test_inductor_ac(convert_compile_load):

    IL2 = 220 / np.pi
    IL3 = 220 / np.pi / np.sqrt(2)

    # Start simulation
    hil.start_simulation()

    # Set sources
    hil.set_source_sine_waveform(name='VAC1', rms=220, frequency=50, phase=90)
    hil.wait_sec(1)

    # Tests
    assert capture.read('IL2') == pytest.approx(IL2, rel=1e-3)
    assert capture.read('IL3') == pytest.approx(IL3, rel=1e-3)

    # Stop simulation
    hil.stop_simulation()



                # UNITED TESTS: 'test_capacitor_dc' AND 'test_capacitor_electrolytic_dc'
# Expected voltages are the same for these two tests
VC1_expected = 50 + 1 / 100e-6 * capture_time
VC2_expected = VC1_expected
@pytest.mark.parametrize("expected_value, source_name, measurement_name",
                         [(VC1_expected, "IDC1",  'VC1'),
                          (VC2_expected, "IDC2", 'VC_el1')])
def test_capacitors_dc(convert_compile_load, expected_value, source_name, measurement_name):

    # Set sources before starting the simulation
    hil.set_source_constant_value(name=source_name, value=1)

    # Set capture
    capture.start_capture(duration=capture_time, rate=1000, signals=[measurement_name],
                          trigger_source="Forced",
                          trigger_use_first_occurence=True,
                          fileName="")

    # Start simulation
    hil.start_simulation()

    # Wait capture to finish
    capture.wait_capture_finish()

    # Stop simulation
    hil.stop_simulation()

    # Evaluate capture results
    cap_data = capture.get_capture_results()
    measurements = cap_data[measurement_name]

    # Calculate the measured voltage after one second
    measurement_value = measurements[-1]

    assert measurement_value == pytest.approx(expected_value, rel=0.01)
    # sig.assert_is_constant(measurements, at_value=around(expected_value, tol_p=0.01))



                # UNITED TESTS: 'test_capacitor_ac' AND 'test_capacitor_electrolytic_ac'
# Expected values are the same for these two tests
VC2 = 10 / (2*np.pi*50*100e-6) * np.sqrt(2)
VC3 = 10 / (2*np.pi*50*100e-6)
VC_el2 = VC2
VC_el3 = VC3
@pytest.mark.parametrize("expected_values, source_name, measurement_names",
                        [([VC2, VC3], 'IAC1', ['VC2', 'VC3']),
                         ([VC_el2, VC_el3], 'IAC2', ['VC_el2', 'VC_el3'])])
def test_capacitors_ac(convert_compile_load, expected_values, source_name, measurement_names):

    # Start simulation
    hil.start_simulation()

    # Set source
    hil.set_source_sine_waveform(name=source_name, rms=10, frequency=50, phase=90)
    hil.wait_msec(1000)

    # cap_data = capture.get_capture_results(wait_capture=False)
    # measurements = cap_data[measurement_names]

    # Test
    for i, expected_value in enumerate(expected_values):
        assert capture.read(measurement_names[i]) == pytest.approx(expected_value, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()