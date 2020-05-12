import os

from model_converter.converter.app.util import get_root_path
from model_converter.converter.parsers.base_parser import BaseParser
from model_converter.converter.app import util
from jinja2 import Environment
from jinja2 import FileSystemLoader

psim_netlist_names_map = {
    'SM_1PH_INV': '1-ph Inverter',
    'SM_3PH_INV': '3-ph Inverter',
    'SM_3PH_3L_T_INV': '3-ph 3-level T-Type Bridge',
    'SM_3PH_3L_NPC_INV': '3-ph 3-level NPC Bridge',
    'SM_3L_NPC_LEG': '3-level NPC Bridge Leg',
    'SM_3L_T_LEG': '3-level T-Type Bridge Leg',
    'SM_2L_LEG': '2-level Bridge Leg',
    'R': 'Resistor',
    'L': 'Inductor',
    'C': 'Capacitor',
    'C_ELECTRO': 'Capacitor (electrolytic)',
    'RHEOSTAT': 'Rheostat',
    'L_SAT': 'Saturable Inductor',
    'RLC': 'RLC',
    'R3': 'R3',
    'L3': 'L3',
    'C3': 'C3',
    'RL3': 'RL3',
    'RC3': 'RC3',
    'RLC3': 'RLC3',
    'MUT2': 'Coupled Inductor (2)',
    'MUT3': 'Coupled Inductor (3)',
    'MUT4': 'Coupled Inductor (4)',
    'CABLE_AC_3PH': '3-ph AC Cable',
    'DIODE': 'Diode',
    'MOSFET': 'MOSFET',
    'IGBT': 'IGBT',
    'THY': 'Thyristor',
    'SSWI': 'Bi-directional Switch',
    'SSWI3': '3-ph Bi-directional Switch',
    'BDIODE1': '1-ph Diode Bridge',
    'BDIODE3': '3-ph Diode Bridge',
    'BTHY1': '1-ph Thyristor Bridge',
    'BTHY3': '3-ph Thyristor Bridge',
    'VSI3': '3-ph Inverter',
    'VSI3_1': 'VSI3 multi-model',
    'TF_IDEAL': 'Ideal Transformer',
    'TF_IDEAL_1': 'Ideal Transformer (Inverted)',
    'TF_1F': '1ph Transformer',
    'TF_1F_1': '1ph Transformer (inverted)',
    'TF_1F_3W': '1-ph 3-w Transformer',
    'TF_1F_4W': '1-ph 4-w Transformer',
    'TF_3YY': '3-ph Y/Y Transformer',
    'TF_3YD': '3-ph Y/D Transformer',
    'TF_3DY': '3-ph D/Y Transformer',
    'TF_3DD': '3-ph D/D Transformer',
    'TF_3YDD': '3-ph 3-w Y/D/D Transformer',
    'TF_3YYD': '3-ph 3-w Y/Y/D Transformer',
    'INDM_3S': 'Squirel-cage Ind. Machine',
    'INDM3_WR': 'Wound-rotor Ind. Machine (linear)',
    'DCM': 'DC Machine',
    'PMSM3': 'PMSM',
    'PMSM3_V': 'PMSM (V)',
    'SYNM3': 'Synchronous Machine',
    'SYNM3_I': 'Synchronous Machine (I)',
    'VP2': 'Voltage Probe',
    'IP': 'Current Probe',
    'V_DC': 'DC Voltmeter',
    'V_AC': 'AC Voltmeter',
    'A_DC': 'DC Ammeter',
    'A_AC': 'AC Ammeter',
    'VSEN': 'Voltage Sensor',
    'ISEN': 'Current Sensor',
    'SOLAR_CELL_PHY': 'Solar Cell',
    'VDC': 'Voltage DC',
    'VDC_CELL': 'Voltage DC (battery)',
    'VSIN': 'Voltage Sine',
    'VSIN3': '3-ph Sine',
    'IDC': 'Current DC',
    'ISIN': 'Current Sine',
    'SM_3L_FLYCAP_LEG': '3-level Flying Cap Inverter Leg',
    'SM_7L_FLYCAP_LEG': '7-level Flying Cap Inverter Leg',
    'CORE_COUPLING_2PH': '1-ph Core Coupling',
    'CORE_COUPLING_3PH': '3-ph Core Coupling',
    'CORE_COUPLING_4PH': '4-ph Core Coupling',
    'CORE_COUPLING_5PH': '5-ph Core Coupling'
}

def generate_psim_doc():
    '''
    This function generates a list of components that are covered by PSIM conversion rules.
    Output of this function is psim_typhoon_compatibility_list.dita file.
    :return:
    '''

    # Insance of BaseParse in order to get the list of compatible components
    baseParser = BaseParser()
    baseParser.rule_file_path = os.path.join(util.get_root_path(),
                                             "conversion_rules",
                                             "psim",
                                             "PSIM_default_rules.ty")
    baseParser.read_rules()

    # Create components list used by the .template file
    components = list()
    for match_rule in baseParser.match_rules:

        if match_rule.source_type in baseParser.patterns.keys():
            psim_type = match_rule.source_type + ' - pattern matching'
        else:
            try:
                psim_type = psim_netlist_names_map[match_rule.source_type]
            except ValueError:
                psim_type = match_rule.source_type

        typhoon_type = match_rule.typhoon_type if match_rule.typhoon_type != 'N-to-M' else 'Subsystem'
        components.append({'psim_type': psim_type,
                           'typhoon_type': typhoon_type})

    # Load the template file
    path = os.path.dirname(os.path.abspath(__file__))

    j2_env = Environment(loader=FileSystemLoader(path),
                         trim_blocks=True)
    template = j2_env.get_template('compatible_components_list.template')

    # Render the template
    rendered_template = template.render(components=components)

    # Write the md file
    file_name = 'psim_typhoon_compatibility_list.dita'

    output_path = get_root_path()

    with open(os.path.join(output_path, file_name), mode='w', encoding='utf-8') as f:
        f.write(rendered_template)

if __name__ == "__main__":
    # execute only if run as a script
    generate_psim_doc()
