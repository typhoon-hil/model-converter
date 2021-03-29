status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'), 'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    %%
    selected_type = get_param(thisBlock,'MachineType');
    mask = Simulink.Mask.get(thisBlock);
    
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'Synchronous Machine', 'PMSM', 'Induction Machine', 'DC Machine'};
                    
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'MachineType','Induction Machine');
    end
    
    %%
    if strcmp(selected_type, 'PMSM')
        pat = 'typhoonPatterns/PMSM';
        inner_component = [getfullname(thisBlock) '/PMSM1'];
    elseif strcmp(selected_type, 'Synchronous Machine')
        pat = 'typhoonPatterns/Synchronous Machine';
        inner_component = [getfullname(thisBlock) '/Synchronous Machine1'];
    elseif strcmp(selected_type, 'DC Machine')
        pat = 'typhoonPatterns/DC Machine';
        inner_component = [getfullname(thisBlock) '/DC Machine1'];
    elseif strcmp(selected_type, 'Induction Machine')
        if sp_ind == true
            pat = 'typhoonPatterns/SP Induction Machine';
            inner_component = [getfullname(thisBlock) '/SP Asynchronous Machine1'];
        else
            pat = 'typhoonPatterns/Induction Machine';
            inner_component = [getfullname(thisBlock) '/Asynchronous Machine1'];
        end
    end
    %%
    model_loaded = get_param(thisBlock, 'model_loaded');
    % If there is a change in the selected topology
    if ~strcmp(old_pat, pat)|strcmp(model_loaded,'on')
        pat_changed = true;
        % Save block position and size
        saved_pos = get_param(thisBlock,'Position');
        % Pattern loading
        bdclose('temp__ptrn');
        dest = getfullname(thisBlock);
        load_system('typhoonPatterns');
        newbd = new_system('temp__ptrn');
        % First clear the subsystem
        Simulink.SubSystem.deleteContents(dest);
        % Copy the contents of the pattern
        Simulink.SubSystem.copyContentsToBlockDiagram(pat, newbd);
        Simulink.BlockDiagram.copyContentsToSubSystem(newbd, dest);
        bdclose('typhoonPatterns');
        bdclose('temp__ptrn');
    else
        pat_changed = false;
    end
    set_param(thisBlock,'old_pat',pat);
    set_param(thisBlock,'model_loaded','off');
    
    %% Update the inner machine mask according to the top-level mask parameters
    
    if strcmp(selected_type, 'PMSM')
        %%
        if strcmp(selected_type, 'Cylindrical')
            set_param(inner_component,'RotorType','Round');             
        elseif strcmp(selected_type, 'Salient Pole')
            set_param(inner_component,'RotorType','Salient-pole');  
        end
        
        if strcmp(theta_ab, '-pi/2')
            set_param(inner_component,'refAngle','90 degrees behind phase A axis (modified Park)');             
        elseif strcmp(theta_ab, '0')
            set_param(inner_component,'refAngle','Aligned with phase A axis (original Park)');  
        end
        
        torque_str = 'Torque Tm';
        speed_str = 'Speed w';

    elseif strcmp(selected_type, 'Synchronous Machine')

        torque_str = 'Mechanical Power Pm'; % power instead of torque
        speed_str = 'Speed w';
        
    elseif strcmp(selected_type, 'DC Machine')
        %%
        set_theta = 1;
        torque_str = 'Torque TL';
        speed_str = 'Speed w';
           
    elseif strcmp(selected_type, 'Induction Machine')
        %%

        if sp_ind == true
            torque_str = 'Torque Tm';
            speed_str = 'Torque Tm'; % No speed option
            
            if strcmp(sp_start_type, 'Split-Phase')
                set_param(inner_component,'MachineType','Split Phase');             
            elseif strcmp(sp_start_type, 'Capacitor-Start')
                set_param(inner_component,'MachineType','Capacitor-Start'); 
            elseif strcmp(sp_start_type, 'Capacitor-Start-Run')
                set_param(inner_component,'MachineType','Capacitor-Start-Run');
            end

        else
            torque_str = 'Torque Tm';
            speed_str = 'Speed w';
            
            if strcmp(RotorType_Ind, 'Squirrel Cage')
                set_param(inner_component,'RotorType','Squirrel-cage');             
            elseif strcmp(RotorType_Ind, 'Double Cage')
                set_param(inner_component,'RotorType','Double Squirrel-cage');  
            end
        end
    end

    if strcmp(loadtype, 'Torque')
        set_param(inner_component,'MechanicalLoad', torque_str);
    elseif strcmp(loadtype, 'Power')
        set_param(inner_component,'MechanicalLoad', torque_str);
    elseif strcmp(loadtype, 'Speed')
        set_param(inner_component,'MechanicalLoad', speed_str);  
    end
    
    set_param([getfullname(thisBlock) '/rate_trans'], 'OutPortSampleTime', num2str(execution_rate));
    
    %%      
    % Description update
    comp_string = selected_type;
    comp_title = mask.getDialogControl('DescTitle');
    comp_title.Prompt = comp_string;
    
    % Only if there was a change in the enable_output parameter there will be
    % an update
    setup_machine_terminals(thisBlock);
    
    description_text = ['(*) Parameters marked with an asterisk have no effect on the MATLAB model, but will be saved when exported to TSE.'];
    mask.set('Description', description_text);
    DescTitle.Visible = 'off';
    
    % Restore block position and size
    if pat_changed
        set_param(thisBlock,'Position', saved_pos);
    end
end
