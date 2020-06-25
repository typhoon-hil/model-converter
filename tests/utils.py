import os, sys
import subprocess
import time

import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model

from model_converter.converter.app.converter import Converter

PSIM_PATH = "C:\\Powersim\\PSIM_2020a_Softkey"
EXPORT_XML = False



######## Intermediate conversion functions

def psim_export_netxml(file_path):
    if EXPORT_XML:
        try:
            # -------------------- Generate psim xml file ---------------------------
            old_path = os.getcwd()
            # Set the directory to PSIM install directory
            os.chdir(PSIM_PATH)
            # Prepare the command
            cmd_string = 'PsimCmd.exe -i "' + file_path + '" -NetXmlU'
            psim_process = subprocess.Popen(cmd_string)
            psim_process.communicate()
            # Set the old path
            os.chdir(old_path)

            psim_process.returncode

            # Retrun code = 0 represents successful export of netlist

            return [psim_process.returncode, file_path[:-7] + 'xml']
        except :
            return [1, None]
    else:
        return [0, file_path[:-7] + 'xml']

def no_intermediate_file(file_path):
    return [0, file_path]

###########

# Generic conversion function
# Conversion types (source_file_format): {"psim","simulink"}
def convert_to_tse(source_file_format, input_file_path):
    converter = Converter(source_file_format, input_file_path)
    tse_path = converter.convert_schema(compile_model=False)[0]
    return tse_path

# TSE compilation and loading
def load_and_compile(tse_path):
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()

def rename_tse_file(tse_path, source_file_format):
    path, extension = tse_path.split('.')
    new_file_path = path + '_' + source_file_format + '.' + extension
    # If the output .tse file already exists, delete it
    if os.path.isfile(new_file_path):
        os.remove(new_file_path)
    os.rename(tse_path, new_file_path)
    return new_file_path

# Currently available conversion types
extensions_dict = {"simulink":".slx", "psim":".psimsch"}
conversion_types = extensions_dict.keys()

# Defines the functions related to an intermediate conversion step, if needed.
intermediate_file_function_dict = {'psim':psim_export_netxml, 'simulink':no_intermediate_file}
