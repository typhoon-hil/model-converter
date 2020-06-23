Currently Simulink and PSIM conversions are possible. The necessary conversion rules can be found in:

* PSIM: model_converter\conversion_rules\psim\PSIM_default_rules.ty
* Simulink: model_converter\conversion_rules\simulink\SIMULINK_default_rules.ty

# Syntax

There are four different types of conversion that can be performed. This section shows the basic structure of each rule type and provides an example at the end. It is important to keep in mind that the syntax is very strict, and missing symbols or incorrect orders can result in errors. Indentation is not mandatory, but recommended.

## One-To-One

A single source component is converted into a single Typhoon HIL component.

### Basic structure

    predicates
    source_component_name => typhoon_component_name:
        list of converted parameter values

        Terminals:
            list of terminal mappings
        ;
    ;

Example sketch:

    @source_property == value
    source_component_name => typhoon_component_name:
        typhoon_component_property_1 = source_property_A;
        typhoon_component_property_2 = "Constant";
        typhoon_component_property_3 = aux_function(argument=source_property_B);

        Terminals:
            typhoon_port[pe] = source_port;
            typhoon_input[sp] = source_input;
        ;
    ;

## One-To-Subsystem

A single source component is converted to a Typhoon HIL subsystem with child components

### Basic structure

    predicates
    source component name => {

        component_1_varname = typhoon_component_name_1:
            list of converted parameter values
        ;

        component_2_varname = typhoon_component_name_2:
            list of converted parameter values
        ;

        component_N_varname = typhoon_component_name_N:
            list of converted parameter values
        ;

        Connections:
            how the defined components are connected inside the subsystem
        ;

        Ports:
            which terminals of the defined components are available as subsystem ports
        ;
    }

Example sketch:

    @source_property == value
    source_component_name => {

        comp_A = typhoon_component_name:
            typhoon_component_property_1 = 10;
        ;

        comp_B = typhoon_component_name:
            typhoon_component_property_1 = source_property_A;
        ;

        Connections:
            comp_A:term2-comp_B:term1,
            comp_A:term4-comp_B:term2,
            comp_A:term6-comp_B:term3,
        ;

        Ports:
            comp_A:term1[pe] = source_port_left1;
            comp_A:term2[pe] = source_port_left2;
            comp_A:term3[pe] = source_port_left3;
            comp_B:term4[pe] = source_port_right1;
            comp_B:term5[pe] = source_port_right2;
            comp_B:term6[pe] = source_port_right3;
        ;
    }



## Pattern-To-One

Multiple source components defined by a pattern rule are converted into a single Typhoon HIL component

### Basic structure

Sketch

## Pattern-To-Subsystem

Multiple source components defined by a pattern rule are converted into a Typhoon HIL subsystem which contains child components

### Basic structure

Sketch

***

## Example rule

Let's view in detail one of the rules currently included in the Simulink conversion rules file.

    @LineType == "PI Section"
    @underground == "off"
    @unit_sys == "Imperial"
    @NumPhases == "3"
    @sequence == "on"
    typhoonHILlib/Transmission Line => core/Transmission Line:
        model = "PI";
        model_def = "Sequence";
        num_of_phases = str2int(str_value=NumPhases);
        unit_sys = lowercase(input_str=unit_sys);
        Length_miles = length_picoup_seq;
        Frequency = f_picoup;
        R_sequence_imperial = r_picoup_seq;
        L_sequence_imperial = l_picoup_seq;
        C_sequence_imperial = c_picoup_seq;

        Terminals:
            a_in[pe] = lconn:1;
            b_in[pe] = lconn:2;
            c_in[pe] = lconn:3;
            d_in[pe] = lconn:4;
            a_out[pe] = rconn:1;
            b_out[pe] = rconn:2;
            c_out[pe] = rconn:3;
            d_out[pe] = rconn:4;
        ;
    ;

In this example rule, the typhoonHILlib Simulink component called **Transmission Line** is converted directly (One-To-One) to Typhoon's **Transmission Line** component. Notice the library path specification before the component names; to convert components from your own libraries you must write the path correctly.

    typhoonHILlib/Transmission Line => core/Transmission Line:

Only **Transmission Line** components with a specific set of parameter values are included in that rule, however. Those values are defined by the predicates

    @LineType == "PI Section"
    @underground == "off"
    @unit_sys == "Imperial"
    @NumPhases == "3"
    @sequence == "on"

This means, for example, that this rule will not apply to a **Transmission Line** component with the *unit_sys* parameter set to *Metric*, or *LineType* set to *Bergeron*.

Next, let's go over the list of parameter values to be included in the conversion. The parameter names to the left are present in Typhoon's **Transmission Line** component.

    model = "PI";
    model_def = "Sequence";

*model* and *model_def* are both ComboBox parameters and are being set directly to string values, which are options in the ComboBoxes.

    num_of_phases = str2int(str_value=NumPhases);
    unit_sys = lowercase(input_str=unit_sys);

For those two parameters, [auxiliary function](https://github.com/typhoon-hil/model-converter/wiki/_new#auxiliary-functions) have to be used. *NumPhases* is not being evaluated by the Simulink component, so a string is passed to the converter (e.g. "3"). Since *num_of_phases* accepts only integer values, the auxiliary function str2int() is used.

In a similar manner, *unit_sys* is a ComboBox parameter with lowercase options. *unit_sys* in the [[typhoonHILlib]] component starts with an uppercase letter, thus the lowercase() auxiliary function is called.

# Predicates

Predicates are used when different rules need to be applied depending on parameter values. The rule will be applied to a component only if every predicate is satisfied (*and* logic).

Consider [[typhoonHILlib]]'s **Rectifier** component and the following rules:

```
@RecType == "Diode"
@ThreePhase == "off"
typhoonHILlib/Rectifier => core/Single Phase Diode Rectifier:

    Terminals:
        a_in[pe] = lconn:1;
        b_in[pe] = lconn:2;
        pos_out[pe] = rconn:1;
        neg_out[pe] = rconn:2;
    ;
;
```

```
@RecType == "Diode"
@ThreePhase == "on"
typhoonHILlib/Rectifier => core/Three Phase Diode Rectifier:

    Terminals:
        a_in[pe] = lconn:1;
        b_in[pe] = lconn:2;
        c_in[pe] = lconn:3;
        pos_out[pe] = rconn:1;
        neg_out[pe] = rconn:2;
    ;
;
```

The *RecType* parameter defines the rectifier type (Diode, Thyristor or Vienna), while the *ThreePhase* parameter toggles between a three-phase or a single-phase model.

We want Typhoon's component to be *core/Single Phase Diode Rectifier* only if *RecType* is set to "Diode". Also, depending on *ThreePhase*, the number of terminals change, so different terminal mappings are needed for each case.


# Auxiliary functions

It may happen that a parameter cannot be mapped directly for several reasons. For example: if the original component has a line voltage parameter, but Typhoon's counterpart has a phase voltage parameter. In such cases auxiliary Python functions can be used/created to perform the correct conversion.

## Viewing available functions or creating new ones

Auxiliary functions are defined in the *model_converter/user_libs/functions.py* file. The example function below solves the previous line/phase voltage problem:

```python
def line_to_phase_rms(line_rms):
    return float(line_rms)/np.sqrt(3)
```

## Calling an auxiliary function

The syntax for calling an auxiliary function is

    aux_func_name(input_parameter=source_property)

Thus, continuing with the aforementioned example

    phase_voltage = line_to_phase_rms(line_rms=line_voltage)

It is important to notice that every function argument must be considered a [keyword argument](https://docs.python.org/3/glossary.html).
