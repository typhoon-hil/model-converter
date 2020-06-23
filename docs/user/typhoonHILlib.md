The **typhoonHILlib** is a library of components created to facilitate the conversion from a [Simulink®](https://www.mathworks.com/products/matlab.html) model to the [Typhoon Schematic Editor](https://www.typhoon-hil.com/products/hil-software/). It contains mask parameters that are included in the conversion process, which reduces drastically (ideally eliminates) the amount of setup needed on the resulting Typhoon schematic after the conversion is done.

# Quickstart Guide

## Installing

1. [Download the library](https://github.com/typhoon-hil/model-converter/raw/master/component_libraries/Simulink/typhoonHILlib.zip)
2. Extract the files to a temporary folder
3. From MATLAB®, run *install_typhoonHILlib.m*
4. Choose a folder for the library installation
5. After the installation you may delete the temporary folder

![Installing](https://user-images.githubusercontent.com/47114530/80837371-09f79b00-8bcd-11ea-9def-a803bc0802b3.png)

## Converting a model

1. Create a new Simulink® model (or modify) with a mix of Simscape Electrical™, Simulink® and Typhoon HIL components. The [[list of supported components|Supported components]] is always growing.

![example_model](https://user-images.githubusercontent.com/47114530/80838557-b6d31780-8bcf-11ea-8ced-eb5c538889bc.png)

2. Add the *Convert to TSE* block from the Typhoon HIL library

![block](https://user-images.githubusercontent.com/47114530/80838099-99517e00-8bce-11ea-8bd3-82b3941a75ad.png)

3. Double-click the component, Select the appropriate options and click *Convert*

![mask](https://user-images.githubusercontent.com/47114530/80838166-c69e2c00-8bce-11ea-88ce-02e523364b35.png)

4. After the conversion is complete, you can open the generated **.tse** file with Typhoon Schematic Editor or the **.cpd** with HIL SCADA, if the *Compile* check box was marked

# Video Example

The following video shows some of the power the conversion brings. Simulink's code generation is used to program a Texas Instruments F2808 control card, and also the model is converted, allowing a quick start of the hardware-in-the-loop simulation.

[step_by_step](https://youtu.be)
