status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;
mask = Simulink.Mask.get(thisBlock);

toggle_init = mask.getParameter('toggle_init');
tog_init = strcmp(toggle_init.Value, 'on');

if strcmp(status, 'stopped')&tog_init&~strcmp(bdroot,'typhoonHILlib')
    
    selected_type = get_param(thisBlock,'LineType');
    num_phases = get_param(gcb, 'NumPhases');
        
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'Bergeron', 'PI Section', 'RL Section', 'Coupled RL'};
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'LineType','PI Section');
    end

    switch selected_type
        
        case 'PI Section'  
            
            underground_typ_ = get_param(gcb, 'underground');
            if strcmp(underground_typ_, 'on')
                pat = ['typhoonPatterns/Cable ' num_phases 'PH'];
            else
                pat = ['typhoonPatterns/PI ' num_phases 'PH'];
            end
            
        case 'RL Section'
            pat = ['typhoonPatterns/RL Section ' num_phases 'PH'];
        
        case 'Coupled RL'
            
            underground_typ_ = get_param(gcb, 'underground');
            if strcmp(underground_typ_, 'on')
                pat = ['typhoonPatterns/Cable ' num_phases 'PH'];
            else
                pat = ['typhoonPatterns/RL Coupled ' num_phases 'PH'];
            end
        
        case 'Bergeron'
            pat = ['typhoonPatterns/Bergeron ' num_phases 'PH'];

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
    
    % Description update
    comp_string = [selected_type ' Transmission Line'];
    comp_title = mask.getDialogControl('DescTitle');
    comp_title.Prompt = comp_string;
    
    description_text = ['In HIL simulation the switches in the contactor are electrically ideal, '...
                        'meaning when closed the resistance is zero, when open the resistance is infinite.<br>'...
                        'Transition time can be defined for both transitions separately.'];
    mask.set('Description', description_text);
    DescTitle.Visible = 'off';
    
    if pat_changed
        % Restore block position and size
        set_param(thisBlock,'Position', saved_pos);
    end
    
    
    param_cell = {  'length_berg', 'rc_berg', 'rg_berg', 'cc_berg', 'ce_berg', 'lc_berg', 'mc_berg'...
                    'length_rl', 'r_rl', 'l_rl', 'length_picoup', 'r_picoup_mat'...
                    'r_picoup_seq', 'l_picoup_mat', 'l_picoup_seq', 'c_picoup_mat', 'c_picoup_seq'};
    units_cell  = { 'length_berg_unit', 'rc_berg_unit', 'rg_berg_unit', 'cc_berg_unit', 'ce_berg_unit', 'lc_berg_unit', 'mc_berg_unit'...
                    'length_rl_unit', 'r_rl_unit', 'l_rl_unit', 'length_picoup_unit', 'r_picoup_mat_unit'...
                    'r_picoup_seq_unit', 'l_picoup_mat_unit', 'l_picoup_seq_unit', 'c_picoup_mat_unit', 'c_picoup_seq_unit'};

    selected_unit_sys = get_param(thisBlock, 'unit_sys');
    last_unit_sys = get_param(thisBlock, 'last_unit_sys');

    if ~strcmp(selected_unit_sys, last_unit_sys)
        if strcmp(selected_unit_sys, 'Imperial')
            metric_to_imperial(param_cell, units_cell);
            set_param(thisBlock, 'last_unit_sys', selected_unit_sys);
        elseif strcmp(selected_unit_sys, 'Metric')
            imperial_to_metric(param_cell, units_cell);
            set_param(thisBlock, 'last_unit_sys', selected_unit_sys);
        end
    end

end


function imperial_to_metric(parameters, units)

    mask = Simulink.Mask.get(gcb);

    current_values = cellfun(@(x) get_param(gcb, x), parameters, 'UniformOutput', false);
    new_values = cellfun(@(x) mat2str(1.609*eval(x), 6), current_values, 'UniformOutput', false);
    cellfun(@(x, y) set_param(gcb, x, y), parameters, new_values);


    diag_ctrls = cellfun(@(x) mask.getDialogControl(x), units, 'UniformOutput', false);
    current_prompts = cellfun(@(x) x.Prompt, diag_ctrls, 'UniformOutput', false);
    cellfun(@(x, y) prompt_func_to_km(x, y), diag_ctrls, current_prompts, 'UniformOutput', false);

    function prompt_func_to_km(diag_ctrl, current_prompt)
        diag_ctrl.Prompt = [current_prompt(1:end-2) 'km'];
    end

end

function metric_to_imperial(parameters, units)

    mask = Simulink.Mask.get(gcb);

    current_values = cellfun(@(x) get_param(gcb, x), parameters, 'UniformOutput', false);
    new_values = cellfun(@(x) mat2str(eval(x)/1.609, 6), current_values, 'UniformOutput', false);
    cellfun(@(x, y) set_param(gcb, x, y), parameters, new_values);

    diag_ctrls = cellfun(@(x) mask.getDialogControl(x), units, 'UniformOutput', false);
    current_prompts = cellfun(@(x) x.Prompt, diag_ctrls, 'UniformOutput', false);
    cellfun(@(x, y) prompt_func_to_mi(x, y), diag_ctrls, current_prompts, 'UniformOutput', false);

    function prompt_func_to_mi(diag_ctrl, current_prompt)
        diag_ctrl.Prompt = [current_prompt(1:end-2) 'mi'];
    end

end

