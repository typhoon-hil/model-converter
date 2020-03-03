import os

from model_converter.converter.app import util
from model_converter.converter.parsers.PSIM_parser import PSIMParser


class Converter:
    """
    Main class of the application. Holds the parser instance reference
     and has the convert_schema method.
    """
    #
    # If no rule file has been defined by the user,
    # the default conversion rules will be applied
    #
    default_rule_file_path = {"PSIM": os.path.join(util.get_root_path(),
                                                   "conversion_rules",
                                                   "psim",
                                                   "PSIM_default_rules.ty")}

    def __init__(self,
                 source_file_format: str,
                 input_file_path: str,
                 rule_file_path: str = None):
        """
        Depending on the parameters, the converter will 
        instantiate the appropriate parser and create the 
        object model from the input file.
        Args:
            source_file_format(str): source file
            input_file_path(str):
            rule_file_path: 
        """
        input_file_path = os.path.abspath(input_file_path)
        if rule_file_path is None:
            rule_file_path = \
                Converter.default_rule_file_path.get(source_file_format.lower())
        if source_file_format == "PSIM":
            self.parser = PSIMParser(input_file_path,
                                     rule_file_path)

        elif source_file_format == "SIMULINK":
            raise InvalidArgumentException("Simulink support not "
                                           "yet implemented.")
        else:
            raise InvalidArgumentException("Model source not supported.")

        self.parser.read_input()
        self.parser.read_rules()

    def convert_schema(self,
                       device_id="HIL604",
                       config_id="1",
                       compile_model=False):
        return self.parser.convert_schema(device_id,
                                          config_id,
                                          compile_model)

class InvalidArgumentException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self, *args, **kwargs)
