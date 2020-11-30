# Typhoon HIL Model Converter

## Intro

The Model Converter is a Python application which is used to convert schematic diagrams from various simulation software tools into Typhoon HIL Schematic file.

This is done by reading the input file, converting each
component found by matching the component type name with
the rule source type name.

## How to use model-converter

In case of PSIM model, model file has to be Netlist XML file exported from PSIM.

### 1. With Graphical Interface(GUI):

Simply call model-converter.exe without any additional arguments.

### 2. From Command Line

model-converter.exe has 6 arguments, 5 of which are optional.

Mandatory argument is:
1. --model(required)- path to the model file to be converted.

Optional arguments are: 
1. --source(optional) – software source of the model where allowed options are PSIM and Simulink. If not set, it will be PSIM as default.
2. --rules(optional)- path to the conversion rules files which will be used when converting components. If not set, default set of conversion rules will be used.
3. --device(optional) – specifies HIL model. If not set, HIL604 will be used as default.
4. --config(optional) – specifies configuration of HIL device. If not set, 1 will be used as default.
5. --compile(optional) – specifies if converted model should be compiles. If not set, it will be set to True as default.

To start model-converter.exe from command line, you have to first go to the folder in which model-converter is saved. 

### Example of calling model-converter.exe from command line:
  ``C:\Users\...\Desktop> model-converter.exe --model path\model.xml``
