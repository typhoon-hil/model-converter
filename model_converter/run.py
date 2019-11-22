import sys
import tkinter

from model_converter.converter.app.converter import Converter, InvalidArgumentException
from model_converter.converter.app.gui.main_window import MainApplication


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            root = tkinter.Tk()
            root.resizable(width=False, height=False)
            MainApplication(root).grid(row=0, column=1)
            root.mainloop()
        else:
            converter = Converter(source_file_format="psim",
                                  input_file_path=sys.argv[1])
            converter.convert_schema()
            print("Done. Check the report.txt file located in "
                  "the source file's folder for more info.")
    except InvalidArgumentException:
        print("\nYou must pass the type of input file you wish to convert."
              " Valid options are:\n\033[1m1) PSIM \n2) ML")