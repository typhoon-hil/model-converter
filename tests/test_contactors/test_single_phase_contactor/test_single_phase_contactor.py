# Imports
import pytest
import os
from pathlib import Path
import tests.utils as utils
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around

# Use VHIL
use_vhil = True

# Name of this test file
test_file_name = Path(__file__).stem
# Folder where this file is located
current_test_dir = os.path.dirname(__file__)
# e.g.: path_and_file = ("test_single_phase_contactor", "path/to/this/directory")
path_and_file = (test_file_name, current_test_dir)

# Parameters used in test_intermediate_conversion
# e.g.: parameter_values = [("simulink","path_and_file"), ("psim","path_and_file"), etc.]
parameter_values = [(type, path_and_file) for type in utils.conversion_types]
# Parameters used in test_conversion_to_tse (calls the test_intermediate_conversion; this fixture is also parametrized)
doubled_parameter_values = [(parameter_values[idx], parameter_values[idx]) for idx in range(len(utils.conversion_types))]

# Intermediate file generation test
@pytest.mark.intermediate_conversion
@pytest.mark.parametrize("create_intermediate_file", parameter_values, indirect=True)
def test_intermediate_conversion(create_intermediate_file):
    return_code, intermediate_file_path = create_intermediate_file
    assert return_code == 0
    assert os.path.isfile(intermediate_file_path)

# Conversion test
@pytest.mark.conversion_to_tse
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
def test_conversion_to_tse(convert_to_tse):
    tse_path = convert_to_tse
    assert os.path.isfile(tse_path)

# Specific test for this file
@pytest.mark.parametrize("VAC, f, s1_closed, iR1_expected",
                         [(220, 50, True, 31.1127),
                          (220, 50, False, 0)])
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
@pytest.mark.parametrize("load_and_compile", [use_vhil], indirect=True)
def test_bi_directional_switch(load_and_compile, VAC, f, s1_closed, iR1_expected):

    # Set source value
    hil.set_source_sine_waveform(name='VAC', rms=VAC, frequency=f)

    # Set switch state
    hil.set_contactor('S1', swControl=True, swState=s1_closed)

    # Start capture
    start_capture(duration=0.04, signals=['iR1'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    iR1 = capture['iR1']

    # Tests
    # Peak
    sig.assert_is_constant(iR1, during=(0.005 - 0.000001, 0.005 + 0.000001), at_value=around(iR1_expected, tol_p=0.01))
    # Half 50 Hz sine
    sig.assert_is_constant(iR1, during=(0.01 - 0.000001, 0.01 + 0.000001), at_value=(-0.02, 0.02))

    # Stop simulation
    hil.stop_simulation()
