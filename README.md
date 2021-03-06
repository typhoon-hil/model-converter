# Typhoon HIL Model Converter

## Intro

The Model Converter is a Python application which is used to convert 
schematic diagrams from various simulation software tools into Typhoon HIL Schematic files.

This is done by reading the input file, converting each component if there is a conversion 
rule written for the component's type.

## How to use model-converter

Model converter supports conversion from Simulink and PSIM to Typhoon HIL. In the case of Simulink models, 
the model file has to be a .slx file. For PSIM models, the model files have to be Netlist XML files exported from PSIM.

### 1. With Graphical Interface (GUI):

Simply call model-converter.exe without any additional arguments.

### 2. From Command Line (CLI):

model-converter.exe has 6 arguments, 5 of which are optional.

Mandatory argument is:
1. --model (required)- path to the model file to be converted.

Optional arguments are: 
1. --source (optional) – software source of the model where allowed options are PSIM and Simulink. If not set, it will be PSIM as default.
2. --rules (optional)- path to the conversion rules files which will be used when converting components. If not set, default set of conversion rules will be used.
3. --device (optional) – specifies HIL model. If not set, HIL604 will be used as default.
4. --config (optional) – specifies configuration of HIL device. If not set, 1 will be used as default.
5. --compile (optional) – specifies if converted model should be compiled. If not set, it will be set to True as default.

To start model-converter.exe from the command line, you have to first go to the folder in which model-converter is saved. 

#### Example of calling model-converter.exe from command line:
  ``C:\Users\...\Desktop>model-converter.exe --model path\model.xml``
  
## For Contributors
  
### Conversion rules 

There are four different types of conversion which can be done:
1. One-To-One - a single source component is converted 
                into a single Typhoon HIL component
2. One-To-Subsystem - a single source component is converted into a
                      Typhoon HIL subsystem which contains child components
3. Pattern-To-One - multiple source components defined by a pattern rule are 
                    converted into a single Typhoon HIL component 
4. Pattern-To-Subsystem - multiple source components defined by a pattern rule
                         are converted into a Typhoon HIL subsystem which contains child components


#### Example of a PSIM One-To-One rule:
    VDC => core/Voltage Source:
        init_source_nature="Constant";
        init_const_value=Amplitude;

        Terminals:
            p_node[pe] = 0;
            n_node[pe] = 1;
        ;
    ;

> **VDC** - source component type name

> **core/Voltage Source** - Typhoon HIL component type name

> **init_source_nature** - Typhoon HIL component property name

> **"Constant"** - literal value of the property
                   (note that literal values are between two double quotation marks)
                   
> **init_const_value** - Typhoon HIL component property name

> **Amplitude** - reference to the source component's property called Amplitude

> **Terminals** - terminal mapping section.
>> **p_node** - name of the Typhoon HIL component's terminal

>> **[pe]** - the type of the Typhoon HIL component's terminal (this can be "pe" or "sp")

>> **0** - the identifier of the source component's terminal (in the case of PSIM, this is the index of the terminal)  
