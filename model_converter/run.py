import sys, os
import argparse
import tkinter
sys.path.append(os.getcwd()) # Added to run in CMD
from model_converter.converter.app.converter import Converter, InvalidArgumentException

from model_converter.converter.app.converter import Converter
from model_converter.converter.app.gui.main_window import MainApplication

HIL_DEVICE_LIST = ["HIL402", "HIL404", "HIL600",
                   "HIL602", "HIL602+", "HIL603",
                   "HIL604"]
SUPPORTED_SOURCES = ["psim", "simulink"]
DEFAULT_CONFIG = 1
DEFAULT_HIL = "HIL604"
DEFAULT_COMPILE = True

def input_is_true(value):
    if type(value) is not str or value.lower() not in ["true", "false"]:
        raise InvalidArgumentException(f"{value} is not a valid value. "
                                       f"Expected True or False.")
    return value.lower() == "true"

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()

    source_sw = ", ".join(SUPPORTED_SOURCES)
    arg_parser.add_argument("--source",
                            help=f"Software source of the model. "
                                 f"Allowed values are {source_sw}."
                                 f"(default: {SUPPORTED_SOURCES[0]})",
                            required=False,
                            choices=SUPPORTED_SOURCES,
                            default=SUPPORTED_SOURCES[0],
                            type=str.lower)

    arg_parser.add_argument("--model",
                            help="Path to the model file "
                                 "which needs to be converted.",
                            required=False,
                            default=None)

    arg_parser.add_argument("--rules",
                            help="Path to the conversion rules file "
                                 "which will be used when converting "
                                 "components.",
                            required=False,
                            default=None)

    dev_str = ", ".join(HIL_DEVICE_LIST)
    arg_parser.add_argument("--device",
                            help=f"HIL device model. "
                                 f"Allowed values are {dev_str}. "
                                 f"(default: {DEFAULT_HIL})",
                            required=False,
                            default="HIL602",
                            choices=HIL_DEVICE_LIST)

    arg_parser.add_argument("--config",
                            help=f"Configuration number "
                                 f"of the HIL device ."
                                 f"(default: {DEFAULT_CONFIG})",
                            required=False,
                            default=DEFAULT_CONFIG)

    arg_parser.add_argument("--compile",
                            help=f"Should the converted model "
                                 f"be compiled? Allowed values are True "
                                 f"or False (default: {DEFAULT_COMPILE})",
                            type=input_is_true,
                            required=False,
                            default=DEFAULT_COMPILE)

    args = arg_parser.parse_args()
    # All args' (Namespace class) attributes are dynamically added
    # and named by the add_argument method of the arg_parser.
    # The .model attribute holds the path to the input model (netlist) file
    if args.model is None:
        root = tkinter.Tk()
        root.resizable(width=False, height=False)
        MainApplication(root).grid(row=0, column=1)
        root.mainloop()
    else:
        converter = Converter(source_file_format=args.source,
                              input_file_path=args.model,
                              rule_file_path=args.rules)
        converter.convert_schema(device_id=args.device,
                                 config_id=args.config,
                                 compile_model=args.compile)
        print("Done. Check the report.txt file located in "
              "the source file's folder for more info.")