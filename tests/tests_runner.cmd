@ECHO off

ECHO Running tests...

REM Change directory to model coverter project root
cd..

REM Select the desired test set to be executed

REM Run all tests
REM python -m pytest .\tests --alluredir=report --open-allure --clean-alluredir

REM Run only PSIM xml export
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m generate_netxml

REM Run only xml to tse cnversion
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m conversion_xml2tse

REM Run PSIM xml export and xml to tse cnversion
REM python -m pytest .\tests\test_psim --alluredir=report --open-allure --clean-alluredir -m "generate_netxml or conversion_xml2tse"

REM Run one test file
python -m pytest .\tests\test_transformers\test_ideal_transformer --alluredir=report --open-allure --clean-alluredir

ECHO:
ECHO:
ECHO ------------------------------------
ECHO -              DONE!               -
ECHO ------------------------------------


PAUSE
