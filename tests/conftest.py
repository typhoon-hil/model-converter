# Imports
import tests.utils as utils
import pytest
import os

@pytest.fixture(scope='session')
def create_intermediate_file(request):
    # In case there is an intermediate file conversion needed (e.g. PSIM to XML)
    # The approppriate function for the source_file_format will be called
    source_file_format, path_and_file = request.param
    test_file_name, current_test_dir = path_and_file
    original_file_path = current_test_dir + '\\' + test_file_name + utils.extensions_dict[source_file_format]
    return utils.intermediate_file_function_dict[source_file_format](original_file_path)

# Conversion of the intermediate file to .tse
@pytest.fixture(scope='session')
def convert_to_tse(create_intermediate_file, request):
    source_file_format, _ = request.param
    _, intermediate_file_path = create_intermediate_file
    tse_path = utils.convert_to_tse(source_file_format, intermediate_file_path)
    return utils.rename_tse_file(tse_path, source_file_format)

# Load and compile the generated .tse file
@pytest.fixture(scope='session')
def load_and_compile(convert_to_tse, request):
    use_vhil = request.param
    tse_path = convert_to_tse
    utils.load_and_compile(tse_path, use_vhil)
