import os
import subprocess
import time

PSIM_PATH = "C:\\Powersim\\PSIM12.0.2_Softkey_X64"
WAIT_TIME = 5 # seconds

def psim_export_netxml(file_path):
    try:
        ## Store the previous path
        #old_path = os.getcwd()
        ## Set the PSIM path
        #os.chdir(PSIM_PATH)
#
        #cmd_string = 'PsimCmd.exe -i "' + file_path + '" -NetXml'
        #psim_process = subprocess.Popen(cmd_string)
        #timeout = time.time() + WAIT_TIME
        #while True:
        #    if time.time() > timeout:
        #        psim_process.terminate()
        #        break
#
        #psim_process.terminate()
#
        ## Set the old path
        #os.chdir(old_path)

        return file_path[:-7] + 'xml'
    except :
        return False

