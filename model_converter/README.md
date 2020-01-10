# Typhoon HIL Model Converter

## Intro

The Model Converter is a Python application which is used
to convert system models from various HIL software
providers into Typhoon HIL's models.

This is done by reading the input file, converting each
component found by matching the component type name with
the rule source type name.

Rule files 

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
