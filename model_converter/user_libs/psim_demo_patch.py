
def psim_demo_patch(full_path):
    import xml.etree.ElementTree as ET

    with open(full_path, encoding='utf-16') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for elem in root.getiterator():
            if 'Name' in elem.attrib:
                # ----------------- PMSM3 parameter mapping ------------------
                if elem.attrib['Name'] == 'Mech. Time Constant':
                    elem.attrib['Name'] = 'Shaft Time Constant'
                if elem.attrib['Name'] == 'Rs (stator resistance)':
                    elem.attrib['Name'] = 'Rs'
                if elem.attrib['Name'] == 'Ld (d-axis ind.)':
                    elem.attrib['Name'] = 'Ld'
                if elem.attrib['Name'] == 'Lq (q-axis ind.)':
                    elem.attrib['Name'] = 'Lq'
                if elem.attrib['Name'] == 'No. of Poles P':
                    elem.attrib['Name'] = 'pms'
                if elem.attrib['Name'] == 'Vpk / krpm':
                    elem.attrib['Name'] = 'Vpk_krpm'

                # --------------- Capacitor parameter mapping ----------------
                if elem.attrib['Name'] == 'Init. Cap. Voltage':
                    elem.attrib['Name'] = 'Initial Voltage'

                # ------- Three Phase Voltage Source parameter mapping -------
                if elem.attrib['Name'] == 'V (line-line-rms)':
                    elem.attrib['Name'] = 'V_line_line_rms'
                if elem.attrib['Name'] == 'Init. Angle (phase A)':
                    elem.attrib['Name'] = 'Initial Angle'

    # re-write the file
    tree.write(full_path, encoding="utf-16")