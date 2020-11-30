# Typhoon HIL Model Converter

## Intro

The Model Converter is a Python application which is used
to convert system models from various HIL software
providers into Typhoon HIL's models.

This is done by reading the input file, converting each
component found by matching the component type name with
the rule source type name.

## How to use model-converter from command line

model-converter.exe has 6 arguments, 5 of which are optional.

Arguments are: 
1. --source(optional) – software source of the model where allowed options are PSIM and Simulink. If not set, it will be PSIM as default.
2. --model(required)- path to the model file to be converted. In case of PSIM model, it has to be Netlist XML file exported from PSIM.
3. --rules(optional)- path to the conversion rules files which will be used when converting components. If not set, default set of conversion rules will be used.
4. --device(optional) – specifies HIL model. If not set, HIL604 will be used as default.
5. --config(optional) – specifies configuration of HIL device. If not set, 1 will be used as default.
6. --compile(optional) – specifies if converted model should be compiles. If not set, it will be set to True as default.

To start model-converter.exe from command line, you have to first go to the folder in which model-converter is saved. 

### Example of calling model-converter.exe from command line:
  C:\Users\Desktop> model-converter.exe --model path\model.xml

## Conversion rules 

There are four different types of conversion which can be done:
1. One-To-One - a single source component is converted 
                into a single Typhoon HIL component
2. One-To-Subsystem - a single source component is converted into a
                      Typhoon HIL subsystem which contains child components
3. Pattern-To-One - multiple source components defined by a pattern rule are 
                    converted into a single Typhoon HIL component 
4. Pattern-To-Subsystem - multiple source components defined by a pattern rule
                         are converted into a Typhoon HIL subsystem which contains child components


### Example of a PSIM One-To-One rule:
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
