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
@pytest.mark.parametrize("Vsin_ydd, Vsin_yyd, f, ss_ydd2_closed, ss_ydd3_closed, ss_yyd2_closed, ss_yyd3_closed, Vydd2_expected,Iydd2_expected, Vydd3_expected,  Iydd3_expected, Vyyd2_expected, Iyyd2_expected, Vyyd3_expected, Iyyd3_expected",
                         [(577.35, 577.35, 50, True, True, True, True, 0, 88.43, 0, 95.859, 0, 51.054, 0, 95.859)])
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
@pytest.mark.parametrize("load_and_compile", [use_vhil], indirect=True)
def test_1_ph_2w_transformer(load_and_compile, Vsin_ydd, Vsin_yyd, f, ss_ydd2_closed, ss_ydd3_closed, ss_yyd2_closed, ss_yyd3_closed, Vydd2_expected,Iydd2_expected, Vydd3_expected,  Iydd3_expected, Vyyd2_expected, Iyyd2_expected, Vyyd3_expected, Iyyd3_expected):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin_ydd', rms=Vsin_ydd, frequency=f)
    hil.set_source_sine_waveform(name='Vsin_yyd', rms=Vsin_yyd, frequency=f)

    hil.set_contactor('ss_ydd2', swControl=True, swState=ss_ydd2_closed)
    hil.set_contactor('ss_ydd3', swControl=True, swState=ss_ydd3_closed)
    hil.set_contactor('ss_yyd2', swControl=True, swState=ss_yyd2_closed)
    hil.set_contactor('ss_yyd3', swControl=True, swState=ss_yyd3_closed)

    # Start capture
    start_capture(duration=0.5, signals=['Vydd2', 'Vydd3', 'Vyyd2', 'Vyyd3','Iydd2', 'Iydd3', 'Iyyd2', 'Iyyd3'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Vydd2 = capture['Vydd2']
    Vydd3 = capture['Vydd3']
    Vyyd2 = capture['Vyyd2']
    Vyyd3 = capture['Vyyd3']
    Iydd2 = capture['Iydd2']
    Iydd3 = capture['Iydd3']
    Iyyd2 = capture['Iyyd2']
    Iyyd3 = capture['Iyyd3']

    # Tests

    sig.assert_is_constant(Vydd2, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vydd2_expected, tol_p=0.01))
    sig.assert_is_constant(Vydd3, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vydd3_expected, tol_p=0.01))
    sig.assert_is_constant(Vyyd2, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vyyd2_expected, tol_p=0.01))
    sig.assert_is_constant(Vyyd3, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vyyd3_expected, tol_p=0.01))
    sig.assert_is_constant(Iydd2, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iydd2_expected, tol_p=0.01))
    sig.assert_is_constant(Iydd3, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iydd3_expected, tol_p=0.01))
    sig.assert_is_constant(Iyyd2, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iyyd2_expected, tol_p=0.01))
    sig.assert_is_constant(Iyyd3, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iyyd3_expected, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()
