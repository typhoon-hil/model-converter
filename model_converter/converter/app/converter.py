import os

from model_converter.converter.app import util
from model_converter.converter.parsers.PSIM_parser import PSIMParser
from model_converter.converter.parsers.Simulink_parser import SimulinkParser


class Converter:

    VERSION = "1.4.4"

    """
    Main class of the application. Holds the parser instance reference
     and has the convert_schema method.
    """
    #
    # If no rule file has been defined by the user,
    # the default conversion rules will be applied
    #
    default_rule_file_path = {"psim": os.path.join(util.get_root_path(),
                                                   "conversion_rules",
                                                   "psim",
                                                   "PSIM_default_rules.ty"),
                              "simulink":
                                  os.path.join(util.get_root_path(),
                                               "conversion_rules",
                                               "simulink",
                                               "SIMULINK_default_rules.ty")}

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
        if source_file_format.lower() == "psim":
            self.parser = PSIMParser(input_file_path,
                                     rule_file_path)

        elif source_file_format.lower() == "simulink":
            self.parser = SimulinkParser(input_file_path,
                                         rule_file_path)
        else:
            raise InvalidArgumentException(f"Model source is not supported ({source_file_format}.")

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
