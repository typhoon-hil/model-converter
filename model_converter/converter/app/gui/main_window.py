import os
import tkinter as tk
from tkinter import ttk, Toplevel
from tkinter.filedialog import askopenfilename
from model_converter.converter.app.util import get_root_path

from typhoon.api.schematic_editor import SchApiException

from model_converter.converter.app.converter import Converter


class MainApplication(tk.Frame):

    icon_file_path = os.path.join("scheme_importer", "app",
                                  "resources", "thil_icon.ico")
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.converter = None
        self.input_file_path = ""

        self.device = "HIL 604"
        self.configuration_id = "1"

        self.config_dialog = None

        self.parent = parent
        self.parent.title("Typhoon HIL Model Converter v1.3")
        self.parent.iconbitmap(default=self.get_icon_path())

        self.file_path_label1 = tk.Label(self,
                                        background="#f0f0f5",
                                        text="Selected file path:",
                                        justify=tk.LEFT)
        self.file_path_label2 = tk.Label(self,
                                         wraplength=650,
                                         background="#f0f0f5",
                                         text="None")
        self.progress_bar = ttk.Progressbar(self,
                                            orient="horizontal",
                                            mode="determinate",
                                            length=650,
                                            maximum=100)
        self.progress_bar.grid(row=2, column=0)
        self.file_path_label1.grid(row=0, column=0)
        self.file_path_label2.grid(row=1, column=0)

        self.report_area = tk.Frame(self,
                                    height=30,
                                    width=85)

        self.report_text = tk.Text(self.report_area,
                                   state="disabled",
                                   padx=15)
        self.report_text.grid(row=0, column=0)
        self.report_area.grid(row=3, column=0, padx=15, pady=15, rowspan=100)

        self.config_btn = tk.Button(self,
                                    text="Set \nHIL \nconfiguration",
                                    width=15,
                                    command=self.on_config_btn_clicked)
        self.config_btn.grid(row=3, column=1)

        self.input_file_btn = tk.Button(self,
                                        text="Select \nXML netlist \nfile",
                                        width=15,
                                        command=self.on_input_file_btn_clicked)

        self.input_file_btn.grid(row=4, column=1, padx=10)


        self.convert_btn = tk.Button(self,
                                     text="Convert \nselected \nfile",
                                     width=15,
                                     state="disabled",
                                     command=self.on_convert_btn_clicked)

        self.convert_btn.grid(row=5, column=1)

    def on_input_file_btn_clicked(self):
        path = askopenfilename(initialdir="/",
                                   title="Select file",
                                   filetypes=(("XML netlist", "*.xml"),
                                              ))
        self.set_input_file_path(path)

    def on_config_btn_clicked(self):
        if self.config_dialog is not None:
            self.config_dialog.top.destroy()
        self.config_dialog = HILConfigDialog(self)
        self.wait_window(self.config_dialog.top)

    def on_convert_btn_clicked(self):
        self.progress_bar.config(value=20)
        self.converter = Converter(source_file_format="psim",
                                   input_file_path=self.input_file_path)
        device = self.device.replace(" ","")
        try:
            tse_path, compiled, report_path = \
                self.converter.convert_schema(device_id=device,
                                              config_id=self.configuration_id,
                                              compile_model=True)

            root_path = get_root_path()
            conversion_log = root_path + "\\conversion.log"
        except SchApiException as ex:
            self.progress_bar.config(value=0)
            self.report_text.config(state="normal")
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert(tk.END, "Error converting selected netlist."
                                    "Please check the validity of the file.")
            self.report_text.config(state="disabled")
            return
        self.progress_bar.config(value=100)
        with open(report_path, "r") as report:
            scrollbar = tk.Scrollbar(self.report_area,
                                     command=self.report_text.yview)
            scrollbar.grid(row=0, column=1, sticky="nsew")
            self.report_text.config(yscrollcommand=scrollbar.set)

            self.report_text.config(state="normal")
            self.report_text.delete('1.0', tk.END)
            valid_report = "--------------------------------\n"
            if compiled:
                valid_report += "Model has been compiled successfully."
            else:
                valid_report += "Model compilation failed."
            valid_report += "\n--------------------------------\n\n"
            self.report_text.insert(tk.END, valid_report)
            self.report_text.insert(tk.END, report.read())
            self.report_text.config(state="disabled")
        with open(conversion_log, "r") as log:
            log_text = log.read()
            # If any errors are present
            if log_text:
                self.report_text.config(state="normal")
                self.report_text.insert(tk.END,
                                        "\n\nDetailed error log\n"
                                        "--------------------------------\n")
                self.report_text.insert(tk.END, log_text)
                self.report_text.config(state="disabled")

    def set_input_file_path(self, path:str):
        if path!="":
            self.progress_bar.config(value=0)
            self.input_file_path = path
            self.convert_btn.config(state="normal")
            self.file_path_label2.config(text=path.replace("/","\\"))

    def get_icon_path(self):
        return os.path.join(self.get_root_path(),
                            "app",
                            "resources", "thil_icon.ico")

    def get_root_path(self):
        return os.path.split(os.path.abspath(os.path.join(
            os.path.realpath(__file__), '..', '..')))[0]


class HILConfigDialog:

    def __init__(self, parent):

        self.top = Toplevel(parent)
        self.top.resizable(width=False, height=False)
        self.top.wm_title("HIL Config")
        self.parent = parent
        x_pos = self.parent.parent.winfo_x()+250
        y_pos = self.parent.parent.winfo_y()+250

        self.top.geometry("%dx%d%+d%+d" % (230, 50, x_pos, y_pos))

        device_lbl = tk.Label(self.top,
                              text="HIL Device")
        device_lbl.grid(row=0,
                        column=0)

        self.device_cb = tk.ttk.Combobox(self.top,
                                         values=["HIL 402", "HIL 602",
                                                 "HIL 602+", "HIL 603",
                                                 "HIL 604"])
        self.device_cb.current(
                            self.device_cb["values"].index(self.parent.device))

        self.device_cb.bind("<<ComboboxSelected>>",
                            self.on_device_cb_selection_changed)
        self.device_cb.grid(row=0,
                            column=1)

        config_lbl = tk.Label(self.top,
                              text="Configuration")
        config_lbl.grid(row=1,
                        column=0)
        self.config_cb = tk.ttk.Combobox(self.top)
        self.on_device_cb_selection_changed(None)
        self.config_cb.current(
            self.config_cb["values"].index(self.parent.configuration_id))

        self.config_cb.bind("<<ComboboxSelected>>",
                            self.on_config_cb_selection_changed)
        self.config_cb.grid(row=1,
                            column=1)

    def on_device_cb_selection_changed(self, event):

        configs_list = ["1", "2",
                        "3", "4"]
        self.parent.device = self.device_cb.get()
        if self.device_cb.get() == "HIL 402":
            configs_list.append("5")
            configs_list.append("6")
            self.config_cb["values"] = configs_list
        elif self.device_cb.get() == "HIL 602":
            self.config_cb["values"] = configs_list
        elif self.device_cb.get() == "HIL 602+":
            configs_list.append("5")
            self.config_cb["values"] = configs_list
        elif self.device_cb.get() == "HIL 603":
            configs_list.append("5")
            self.config_cb["values"] = configs_list
        elif self.device_cb.get() == "HIL 604":
            configs_list.append("5")
            self.config_cb["values"] = configs_list
        if self.parent.configuration_id not in configs_list:
            self.config_cb.current(0)
            self.parent.configuration_id = self.config_cb.get()

    def on_config_cb_selection_changed(self, event):
        self.parent.configuration_id = self.config_cb.get()


if __name__ == "__main__":
    root = tk.Tk()

    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()