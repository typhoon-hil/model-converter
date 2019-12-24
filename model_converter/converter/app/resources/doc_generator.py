import os

from model_converter.converter.app.util import get_root_path
from model_converter.converter.parsers.base_parser import BaseParser
from model_converter.converter.app import util
from jinja2 import Environment
from jinja2 import FileSystemLoader


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
