status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'TransfType');
        
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {   'Single-Phase Ideal', 'Single-Phase Two Windings', 'Single-Phase Three Windings'...
                        'Single-Phase Four Windings', 'Three-Phase Two Windings', 'Three-Phase Three Windings'};
                    
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'TransfType','Single-phase Ideal');
    end

    switch selected_type
        case 'Single-Phase Ideal'
            pat = 'typhoonPatterns/Ideal Transformer';
        case 'Single-Phase Two Windings'
            pat = 'typhoonPatterns/SP 2W Transformer';
        case 'Single-Phase Three Windings'
            pat = 'typhoonPatterns/SP 3W Transformer';
        case 'Single-Phase Four Windings'
            pat = 'typhoonPatterns/SP 4W Transformer';               
        case 'Three-Phase Two Windings'
            pat = 'typhoonPatterns/TP 2W Transformer';               
        case 'Three-Phase Three Windings'
            pat = 'typhoonPatterns/TP 3W Transformer';                    
    end
    
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
    
    % Name of the inside transformer
    t_component = [getfullname(thisBlock) '/T1'];
    
    if ~strcmp(selected_type, 'Single-Phase Ideal')
        
        % Update the inner transformer mask according to the top-level mask parameters
        
        % Saturation
        sat_toggle = get_param(thisBlock, 'sat_toggle');
        if strcmp(sat_toggle,'on')
            sat_array = transpose([str2num(num2str(i_vec)); str2num(num2str(flux_vec))]);
            sat_str_int = '';
            for i = 1:size(flux_vec, 2)
                sat_str_int = [sat_str_int, num2str(sat_array(i,:)), '; '];
            end
            set_param(t_component, 'SetSaturation', 'on');  
            sat_string = ['[', sat_str_int,']'];
            set_param(t_component, 'Saturation', sat_string);
        else
            set_param(t_component, 'SetSaturation', 'off');
        end
        
        % V, R, L
        units = get_param(thisBlock, 'units');
        if strcmp(units,'SI')
            set_param(t_component, 'UNITS', 'SI');
        else
            set_param(t_component, 'UNITS', 'PU');
        end
     
        if ~strcmp(selected_type, 'Three-Phase Two Windings')&~strcmp(selected_type, 'Three-Phase Three Windings')
            switch selected_type
                case 'Single-Phase Two Windings'
                    volt_string = ['[' num2str(V1) ' ' num2str(V2) ']'];
                    res_string = ['[' num2str(R1) ' ' num2str(R2) ']'];
                    ind_string = ['[' num2str(L1) ' ' num2str(L2) ']']; 
                case 'Single-Phase Three Windings'
                    volt_string = ['[' num2str(V1) ' ' num2str(V2)  ' ' num2str(V3) ']'];
                    res_string = ['[' num2str(R1) ' ' num2str(R2) ' ' num2str(R3)  ']'];
                    ind_string = ['[' num2str(L1) ' ' num2str(L2) ' ' num2str(L3)  ']']; 
                case 'Single-Phase Four Windings'
                    volt_string = ['[' num2str(V1) ' ' num2str(V2)  ' ' num2str(V3)  ' ' num2str(V4) ']'];
                    res_string = ['[' num2str(R1) ' ' num2str(R2) ' ' num2str(R3)  ' ' num2str(R4)   ']'];
                    ind_string = ['[' num2str(L1) ' ' num2str(L2) ' ' num2str(L3)  ' ' num2str(L4)   ']'];               
            end
        
            set_param(t_component, 'NominalVoltages', volt_string);
            set_param(t_component, 'WindingResistances', res_string);
            set_param(t_component, 'WindingInductances', ind_string);
                   
        else
            wind1_string = ['[' num2str(V1) ' ' num2str(R1) ' ' num2str(L1) ']'];
            wind2_string = ['[' num2str(V2) ' ' num2str(R2) ' ' num2str(L2) ']'];
            wind3_string = ['[' num2str(V3) ' ' num2str(R3) ' ' num2str(L3) ']'];
            
            % Connections (Y, D)
            conn1 = get_param(thisBlock, 'conn_1');
            conn2 = get_param(thisBlock, 'conn_2');
            conn3 = get_param(thisBlock, 'conn_3');
            
            if strcmp(conn1, 'Wye')
                wind1_conn = 'Yg';
            else
                wind1_conn = 'Delta (D1)';
            end
                
            if strcmp(conn2, 'Wye')
                wind2_conn = 'Yg';
            else
                wind2_conn = 'Delta (D1)';
            end
                
            if strcmp(conn3, 'Wye')
                wind3_conn = 'Yg';
            else
                wind3_conn = 'Delta (D1)';
            end
            
            set_param(t_component, 'winding1', wind1_string);
            set_param(t_component, 'Winding1Connection', wind1_conn);
            set_param(t_component, 'winding2', wind2_string);
            set_param(t_component, 'Winding2Connection', wind2_conn);
            if strcmp(selected_type, 'Three-Phase Three Windings')
                set_param(t_component, 'winding3', wind3_string);
                set_param(t_component, 'Winding3Connection', wind3_conn);
            end

        end
          
        set_param(t_component, 'Lm', num2str(Lm));
        set_param(t_component, 'Rm', num2str(Rm));
        set_param(t_component, 'NominalPower', ['[' num2str(Sn) ' ' num2str(fn) ']']);    
        
    else
        set_param(t_component, 'winding1', ['[' num2str(n1) ' 0 0]']);
        set_param(t_component, 'winding2', ['[' num2str(n2) ' 0 0]']);
    end
    
    
    % Description update
    comp_string = [selected_type ' Transformer'];
    comp_title = mask.getDialogControl('DescTitle');
    comp_title.Prompt = comp_string;
    
    description_text = [''];
    mask.set('Description', description_text);
    DescTitle.Visible = 'off';
    
    if pat_changed
        % Restore block position and size
        set_param(thisBlock,'Position', saved_pos);
    end
end
