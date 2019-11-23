# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
import typhoon.test.capture as capture
import pytest
import numpy as np
import os
import logging
from model_converter.converter.app.converter import Converter
import typhoon.test.signals as signal
logger = logging.getLogger(__name__)

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\rlc_branches\\rlc_components_1_1\\rlc_components_1_1.xml'

tse_path = os.path.join(psim_tests_dir, "references", "rlc_branches", "rlc_components_1_1", "rlc_components_1_1.tse")
cpd_path = psim_tests_dir + \
           "\\references\\rlc_branches\\rlc_components_1_1\\rlc_components_1_1 Target files\\rlc_components_1_1.cpd"


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    ###################################################
    # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)

    # # Start simulation
    # hil.start_simulation()


@pytest.mark.parametrize("VDC, Vin, Vout, I", [
    (100.0, 100.0, 80.0, 2.0),
    # (-100.0, -100.0, -80.0, -2.0),
    # (50.0, 50.0, 40.0, 1.0)
])
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


@pytest.mark.parametrize("VDC1, L1, IL1_0", [(100, 10e-3, 50)])
def test_inductor_dc(convert_compile_load, VDC1, L1, IL1_0):

    # Set sources before starting the simulation
    hil.set_source_constant_value(name='VDC1', value=VDC1)

    # Start capture
    channel_list = ["IL1"]
    capture_time = 0.01

    # Expected current
    IL1_expected = VDC1 * capture_time / L1 + IL1_0

    capture.start_capture(duration=capture_time,
                          rate=1000,
                          signals=channel_list,
                          trigger_source="Forced",
                          trigger_use_first_occurence=True,
                          fileName="")

    # Start simulation
    hil.start_simulation()

    # Wait capture to finish()
    capture.wait_capture_finish()

    # Stop simulation
    hil.stop_simulation()

    # Evaluate capture results
    meas_res = capture.get_capture_results()
    measurements = meas_res["IL1"]

    # Calculate the measured current after one second
    IL1_measured = measurements[-1]

    # Check if captured current ise the ramp with the last value equal to the I_l_expected
    slope = VDC1 / L1  # slope of the linear voltage growth
    tolerance = 0.01 * IL1_expected
    assert signal.is_ramp(measurements, slope=slope, tol=tolerance)
    assert IL1_measured == pytest.approx(IL1_expected, abs=tolerance)


@pytest.mark.parametrize("VAC1, theta, f",
                         [(220, 90, 50)])
def test_inductor_ac(convert_compile_load, VAC1, theta, f):

    # Maybe delete?
    # # Set sources before starting the simulation
    # hil.set_source_sine_waveform("VAC1", VAC1, f, theta)

    IL2 = VAC1 / np.pi
    IL3 = VAC1 / np.pi / np.sqrt(2)

    # Start simulation
    hil.start_simulation()

    # Set sources
    hil.set_source_sine_waveform(name='VAC1', rms=VAC1, frequency=f, phase=theta)
    hil.wait_sec(1)

    # Tests
    assert capture.read('IL2') == pytest.approx(IL2, rel=1e-3)
    assert capture.read('IL3') == pytest.approx(IL3, rel=1e-3)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("IDC1, C1, VC1_0", [(1, 100e-6, 50)])
def test_capacitor_dc(convert_compile_load, IDC1, C1, VC1_0):

    # Set sources before starting the simulation
    hil.set_source_constant_value(name="IDC1", value=IDC1)

    # Set capture
    channel_list = ["VC1"]
    capture_time = 0.01

    # Expexted voltage
    VC1_expected = VC1_0 + IDC1 / C1 * capture_time

    capture.start_capture(duration=capture_time,
                          rate=1000,
                          signals=channel_list,
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
    meas_res = capture.get_capture_results()
    measurements = meas_res["VC1"]

    # Calculate the measured voltage after one second
    VC1_measured = measurements[-1]

    assert VC1_measured == pytest.approx(VC1_expected, rel=0.01)


@pytest.mark.parametrize("IAC1, theta, f, C2, C3", [(10, 90, 50, 100e-6, 100e-6)])
def test_capacitor_ac(convert_compile_load, IAC1, theta, f, C2, C3):

    VC2 = IAC1 / (2*np.pi*f*C2) * np.sqrt(2)
    VC3 = IAC1 / (2*np.pi*f*C3)

    # Start simulation
    hil.start_simulation()

    # Set source
    hil.set_source_sine_waveform(name='IAC1', rms=IAC1, frequency=f, phase=theta)
    hil.wait_msec(1000)

    # Test
    assert capture.read('VC2') == pytest.approx(expected=VC2, rel=1e-2)
    assert capture.read('VC3') == pytest.approx(expected=VC3, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("IDC2, C_el1, VC_el1_0", [(1, 100e-6, 50)])
def test_capacitor_electrolytic_dc(convert_compile_load, IDC2, C_el1, VC_el1_0):

    # Set sources before starting the simulation
    hil.set_source_constant_value(name="IDC2", value=IDC2)

    # Set capture
    channel_list = ["VC_el1"]
    capture_time = 0.01

    # Expected voltage
    VC_el1_expected = VC_el1_0 + IDC2 / C_el1 * capture_time

    capture.start_capture(duration=capture_time,
                          rate=1000,
                          signals=channel_list,
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
    meas_res = capture.get_capture_results()
    measurements = meas_res["VC_el1"]

    # Calculate the measured voltage after one second
    VC1_measured = measurements[-1]

    assert VC1_measured == pytest.approx(VC_el1_expected, rel=0.01)


@pytest.mark.parametrize("IAC2, theta, f, C2, C3", [(10, 90, 50, 100e-6, 100e-6)])
def test_capacitor_electrolytic_ac(convert_compile_load, IAC2, theta, f, C2, C3):

    VC_el2 = IAC2 / (2*np.pi*f*C2) * np.sqrt(2)
    VC_el3 = IAC2 / (2*np.pi*f*C3)

    # Start simulation
    hil.start_simulation()

    # Set source
    hil.set_source_sine_waveform(name='IAC2', rms=IAC2, frequency=f, phase=theta)
    hil.wait_msec(1000)

    # Test
    assert capture.read('VC_el2') == pytest.approx(expected=VC_el2, rel=1e-2)
    assert capture.read('VC_el3') == pytest.approx(expected=VC_el3, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


