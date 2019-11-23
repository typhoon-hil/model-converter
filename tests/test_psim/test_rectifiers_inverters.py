# Imports
import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
from typhoon.test.capture import start_capture, get_capture_results
import pytest
import numpy as np
import os
from model_converter.converter.app.converter import Converter

vhil = True

# Define the paths
psim_tests_dir = os.path.dirname(__file__)
tests_dir = os.path.dirname(psim_tests_dir)
sch_importer_dir = os.path.dirname(tests_dir)

netlist_path = psim_tests_dir + '\\references\\switches\\rectifiers_inverters\\rectifiers_inverters.xml'


@pytest.fixture(scope='session')
def convert_compile_load():
    # Comment this if don't wont to compile model again

    # ###################################################
    # # Convert the model
    converter = Converter("psim", netlist_path)
    tse_path = converter.convert_schema(compile_model=False)
    cpd_path = tse_path[:-4] + " Target files\\" + tse_path.split("\\")[-1][:-4] + ".cpd"
    # Open the converted tse file
    model.load(tse_path)
    # Compile the model
    model.compile()
    ###################################################

    # Load to VHIL
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=vhil)


@pytest.mark.parametrize("Vdb, f", [(220, 50)])
def test_diode_bridge(convert_compile_load, Vdb, f):

    # Set source value.
    hil.set_source_sine_waveform(name='Vdb', rms=Vdb, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['Idb_ac', 'Idb_dc'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Idb_ac = np.mean(capture['Idb_ac'])
    Idb_dc = np.mean(capture['Idb_dc'])

    # Expected currents
    R = 10.0
    Idb_ac_exp = Vdb/R
    Idb_dc_exp = Vdb/R*2*np.sqrt(2)/np.pi

    # Tests
    assert Idb_ac == pytest.approx(Idb_ac_exp, rel=1e-2)
    assert Idb_dc == pytest.approx(Idb_dc_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("V3ph_db, f", [(220, 50)])
def test_3ph_diode_bridge(convert_compile_load, V3ph_db, f):

    # Set source value.
    hil.set_source_sine_waveform(name='V3ph_db', rms=V3ph_db, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['I3ph_db_ac', 'I3ph_db_dc'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    I3ph_db_ac = np.mean(capture['I3ph_db_ac'])
    I3ph_db_dc = np.mean(capture['I3ph_db_dc'])

    # Expected currents
    R = 10.0
    I3ph_db_ac_exp = V3ph_db/R*np.sqrt(2)*1.654
    I3ph_db_dc_exp = V3ph_db/R*np.sqrt(2)*1.655

    # Tests
    assert I3ph_db_ac == pytest.approx(I3ph_db_ac_exp, rel=1e-2)
    assert I3ph_db_dc == pytest.approx(I3ph_db_dc_exp, rel=1e-2)

    # Stop simulation
    hil.stop_simulation()


@pytest.mark.parametrize("Vtb, f, ss_tb",
                         [(220, 50, 0),
                          (220, 50, 1)])
def test_thyristor_bridge(convert_compile_load, Vtb, f, ss_tb):

    # Set source value.
    hil.set_source_sine_waveform(name='Vtb', rms=Vtb, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['Itb_ac', 'Itb_dc'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Set switch state
    hil.set_pe_switching_block_control_mode(blockName='BT1', switchName='Sa_bot',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT1', switchName='Sa_bot',
                                              value=ss_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT1', switchName='Sa_top',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT1', switchName='Sa_top',
                                              value=ss_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT1', switchName='Sb_bot',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT1', switchName='Sb_bot',
                                              value=ss_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT1', switchName='Sb_top',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT1', switchName='Sb_top',
                                              value=ss_tb)

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Itb_ac = np.mean(capture['Itb_ac'])
    Itb_dc = np.mean(capture['Itb_dc'])

    # Expected currents
    R = 10.0
    if ss_tb == 1:
        Itb_ac_exp = Vtb/R
        Itb_dc_exp = Vtb/R*2*np.sqrt(2)/np.pi
    else:
        Itb_ac_exp = 0
        Itb_dc_exp = 0

    # Stop simulation
    hil.stop_simulation()

    # Tests
    assert Itb_ac == pytest.approx(Itb_ac_exp, rel=1e-2, abs=0.2)
    assert Itb_dc == pytest.approx(Itb_dc_exp, rel=1e-2, abs=0.2)


@pytest.mark.parametrize("V3ph_tb, f, ss_3ph_tb",
                         [(220, 50, 0),
                          (220, 50, 1)])
def test_3ph_thyristor_bridge(convert_compile_load, V3ph_tb, f, ss_3ph_tb):

    # Set source value.
    hil.set_source_sine_waveform(name='V3ph_tb', rms=V3ph_tb, frequency=f)

    # Start capture
    start_capture(duration=0.1, signals=['I3ph_tb_ac', 'I3ph_tb_dc'], executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Set switch state
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sa_bot',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sa_bot',
                                              value=ss_3ph_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sa_top',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sa_top',
                                              value=ss_3ph_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sb_bot',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sb_bot',
                                              value=ss_3ph_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sb_top',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sb_top',
                                              value=ss_3ph_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sc_bot',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sc_bot',
                                              value=ss_3ph_tb)
    hil.set_pe_switching_block_control_mode(blockName='BT32', switchName='Sc_top',
                                            swControl=True)
    hil.set_pe_switching_block_software_value(blockName='BT32', switchName='Sc_top',
                                              value=ss_3ph_tb)

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    I3ph_tb_ac = np.mean(capture['I3ph_tb_ac'])
    I3ph_tb_dc = np.mean(capture['I3ph_tb_dc'])

    # Expected currents
    R = 10.0
    if ss_3ph_tb == 1:
        I3ph_tb_ac_exp = V3ph_tb / R * np.sqrt(2) * 1.654
        I3ph_tb_dc_exp = V3ph_tb / R * np.sqrt(2) * 1.655
    else:
        I3ph_tb_ac_exp = 0
        I3ph_tb_dc_exp = 0

    # Stop simulation
    hil.stop_simulation()

    # Tests
    assert I3ph_tb_ac == pytest.approx(I3ph_tb_ac_exp, rel=1e-2, abs=0.2)
    assert I3ph_tb_dc == pytest.approx(I3ph_tb_dc_exp, rel=1e-2, abs=0.2)




