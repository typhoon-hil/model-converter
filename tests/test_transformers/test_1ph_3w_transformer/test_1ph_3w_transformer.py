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
# e.g.: path_and_file = ("test_three_phase_contactor", "path/to/this/directory")
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
@pytest.mark.parametrize("Vt3w, f, ss3_closed, ss4_closed, Vt_3w_2_ac_expected, Vt_3w_3_ac_expected, It_3w_3_ac_expected,It_3w_2_ac_expected",
                         [(110, 50, True, True, 0, 0, 550.12, 824.9)])
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
@pytest.mark.parametrize("load_and_compile", [use_vhil], indirect=True)
def test_1ph_3w_transformer(load_and_compile, Vt3w, f, ss3_closed, ss4_closed, Vt_3w_2_ac_expected, Vt_3w_3_ac_expected, It_3w_2_ac_expected,It_3w_3_ac_expected):

    # Set source value
    hil.set_source_sine_waveform(name='Vt3w', rms=Vt3w, frequency=f)

    # Set switch state
    hil.set_contactor('SS3', swControl=True, swState=ss3_closed)
    hil.set_contactor('SS4', swControl=True, swState=ss4_closed)

    # Start capture
    start_capture(duration=0.9, signals=['Vt_3w_2_ac', 'Vt_3w_3_ac', 'It_3w_2_ac', 'It_3w_3_ac'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Vt_3w_2_ac = capture['Vt_3w_2_ac']
    Vt_3w_3_ac = capture['Vt_3w_3_ac']
    It_3w_2_ac = capture['It_3w_2_ac']
    It_3w_3_ac = capture['It_3w_3_ac']

    # Tests

    sig.assert_is_constant(Vt_3w_2_ac, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vt_3w_2_ac_expected, tol_p=0.01))
    sig.assert_is_constant(Vt_3w_3_ac, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vt_3w_3_ac_expected, tol_p=0.01))

    sig.assert_is_constant(It_3w_2_ac, during=(0.8 - 0.0001, 0.8 + 0.0001), at_value=around(It_3w_2_ac_expected, tol_p=0.02))
    sig.assert_is_constant(It_3w_2_ac, during=(0.81 - 0.0001, 0.81 + 0.0001), at_value=around(-It_3w_2_ac_expected, tol_p=0.02))


    sig.assert_is_constant(It_3w_3_ac, during=(0.8 - 0.0001, 0.8 + 0.0001), at_value=around(-It_3w_3_ac_expected, tol_p=0.02))
    sig.assert_is_constant(It_3w_3_ac, during=(0.81 - 0.0001, 0.81 + 0.0001), at_value=around(It_3w_3_ac_expected, tol_p=0.02))

    # Stop simulation
    hil.stop_simulation()
