@ECHO off

ECHO Running tests...

REM Select the desired test set to be executed

REM Run all psim tests
python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir

REM Run one test file
REM python -m pytest .\tests\test_psim\test_1ph_2w_transformer\test_single_ph_2w_transformer.py --alluredir=report --open-allure --clean-alluredir

ECHO:
ECHO:
ECHO ------------------------------------
ECHO -              DONE!               -
ECHO ------------------------------------


PAUSE
