import os
import subprocess
import time

PSIM_PATH = "C:\\Powersim\\PSIM12.0.3_Softkey_X64"
EXPORT_XML = False

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

