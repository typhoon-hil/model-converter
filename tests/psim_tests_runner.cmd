@ECHO off

ECHO Running tests...

REM Change directory to model coverter project root
cd..

REM Select the desired test set to be executed

REM Run all psim tests
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir

REM Run only PSIM xml export
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m generate_netxml

REM Run only xml to tse cnversion
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m conversion_xml2tse

REM Run PSIM xml export and xml to tse cnversion
python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m "generate_netxml or conversion_xml2tse"

REM Run one test file
REM python -m pytest .\tests\test_psim\test_1ph_2w_transformer\test_single_ph_2w_transformer.py --alluredir=report --open-allure --clean-alluredir

ECHO:
ECHO:
ECHO ------------------------------------
ECHO -              DONE!               -
ECHO ------------------------------------


PAUSE
