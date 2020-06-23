This [[devpage]] contains a step-by-step example of the process involved in the creation of a new [[typhoonHILlib]] component and linking to a Typhoon Schematic Editor (TSE) component.

# 1. Straight rule creation

Some Simulink components such as the *Voltage Source* have a direct TSE counterpart. In those cases, simply creating a rule for the conversion is enough.

    powerlib/Electrical Sources/DC Voltage Source => core/Voltage Source:
        init_source_nature="Constant";
        init_const_value=Amplitude;

    	Terminals:
    		p_node[pe] = rconn:1;
    		n_node[pe] = lconn:1;
    	;
    ;

This rule instructs the converter to create a **core/Voltage Source** for every **powerlib/Electrical Sources/DC Voltage Source** detected and set the relevant properties. More details on rule creation can be found [[here|Writing conversion rules]].


# 2. Creating a new Simulink block

## Creating a masked Subsystem block

new Subsystem
create mask
add parameters

## Auxiliary files

### Image initialization

### Block initialization file

Create a block initialization file named **block_name_init.m**.

What is the initialization for, when to use it
Link to matlab documentation

### MaskCallback file

Create a MaskCallback file named **block_name_callback.m**. When the change of a mask parameter must have immediate effects on the mask, this file should be called. For example: we want the CheckBox "a" to appear only when "c" is selected
careful with set_param()

1. Create a Subsystem component

# General guidelines and information


# 3. Modifying a [[typhoonHILlib]] block

suppose you want to add a new converter to the DC-DC Converter block
