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
@pytest.mark.parametrize("Vsin_yy, Vsin_dd, Vsin_yd, Vsin_dy, f, ss_yy_closed, ss_dd_closed, ss_yd_closed, ss_dy_closed, Vyy_expected, Iyy_expected, Vdd_expected, Idd_expected, Vyd_expected, Iyd_expected, Vdy_expected, Idy_expected",
                         [(288.67, 288.67, 288.67, 288.67, 50, True, True, True, True, 0, 352.17,  0, 1056.05,  0, 609.83, 0, 609.83)])
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
@pytest.mark.parametrize("load_and_compile", [use_vhil], indirect=True)
def test_3ph_2w_transformer(load_and_compile, Vsin_yy, Vsin_dd, Vsin_yd, Vsin_dy, f, ss_yy_closed, ss_dd_closed, ss_yd_closed, ss_dy_closed, Vyy_expected, Iyy_expected, Vdd_expected, Idd_expected, Vyd_expected, Iyd_expected, Vdy_expected, Idy_expected):

    # Set source value
    hil.set_source_sine_waveform(name='Vsin_yy', rms=Vsin_yy, frequency=f)
    hil.set_source_sine_waveform(name='Vsin_dd', rms=Vsin_dd, frequency=f)
    hil.set_source_sine_waveform(name='Vsin_yd', rms=Vsin_yd, frequency=f)
    hil.set_source_sine_waveform(name='Vsin_dy', rms=Vsin_dy, frequency=f)

    hil.set_contactor('SS_yy', swControl=True, swState=ss_yy_closed)
    hil.set_contactor('SS_dd', swControl=True, swState=ss_dd_closed)
    hil.set_contactor('SS_yd', swControl=True, swState=ss_yd_closed)
    hil.set_contactor('SS_dy', swControl=True, swState=ss_dy_closed)

    # Start capture
    start_capture(duration=0.5, signals=['Vyy', 'Vyd', 'Vdy', 'Vdd','Iyy', 'Iyd','Idy', 'Idd'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Vyy = capture['Vyy']
    Vyd = capture['Vyd']
    Vdy = capture['Vdy']
    Vdd = capture['Vdd']
    Iyy = capture['Iyy']
    Iyd = capture['Iyd']
    Idy = capture['Idy']
    Idd = capture['Idd']

    # Tests

    sig.assert_is_constant(Vyy, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vyy_expected, tol_p=0.01))
    sig.assert_is_constant(Vyd, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vyd_expected, tol_p=0.01))
    sig.assert_is_constant(Vdy, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vdy_expected, tol_p=0.01))
    sig.assert_is_constant(Vdd, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Vdd_expected, tol_p=0.01))
    sig.assert_is_constant(Iyy, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iyy_expected, tol_p=0.01))
    sig.assert_is_constant(Iyd, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Iyd_expected, tol_p=0.01))
    sig.assert_is_constant(Idy, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Idy_expected, tol_p=0.01))
    sig.assert_is_constant(Idd, during=(0.41 - 0.0001, 0.41 + 0.0001), at_value=around(Idd_expected, tol_p=0.01))

    # Stop simulation
    hil.stop_simulation()
