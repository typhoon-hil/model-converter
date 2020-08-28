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
@pytest.mark.parametrize("VDC1, VDC2, iA_expected, iB_expected,iC_expected",
                         [(75, 75, 10, -10, -5)])
@pytest.mark.parametrize("convert_to_tse, create_intermediate_file", doubled_parameter_values, indirect=True)
@pytest.mark.parametrize("load_and_compile", [use_vhil], indirect=True)
def test_three_phase_T_type_converter(load_and_compile, VDC1,VDC2, iA_expected, iB_expected,iC_expected):

    # Set source value
    hil.set_source_constant_value(name='VDC1', value=VDC1)
    hil.set_source_constant_value(name='VDC2', value=VDC2)
    for switch in range(1, 5):

        hil.set_pe_switching_block_control_mode(blockName='Ttype',
                                                  switchName="Sa_" + str(switch),
                                                  swControl=True)
        hil.set_pe_switching_block_software_value(blockName='Ttype',
                                                  switchName="Sa_" + str(switch),
                                                  value=1)
        hil.set_pe_switching_block_control_mode(blockName='Ttype',
                                                  switchName="Sb_" + str(switch),
                                                  swControl=True)
        hil.set_pe_switching_block_software_value(blockName='Ttype',
                                                  switchName="Sb_" + str(switch),
                                                  value=1)
        hil.set_pe_switching_block_control_mode(blockName='Ttype',
                                                  switchName="Sc_" + str(switch),
                                                  swControl=True)
        hil.set_pe_switching_block_software_value(blockName='Ttype',
                                                  switchName="Sc_" + str(switch),
                                                  value=1)
    # Start capture
    start_capture(duration=0.04, signals=['iA', 'iB', 'iC'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    iA = capture['iA']
    iB = capture['iB']
    iC = capture['iC']

    # Tests
    sig.assert_is_constant(iA, during=(0.015 - 0.001, 0.015 + 0.001), at_value=around(iA_expected, tol_p=0.01))

    sig.assert_is_constant(iB, during=(0.015 - 0.001, 0.015 + 0.001), at_value=around(iB_expected, tol_p=0.01))

    sig.assert_is_constant(iC, during=(0.03 - 0.001, 0.03 + 0.001), at_value=around(iC_expected, tol_p=0.01))


    # Stop simulation
    hil.stop_simulation()
