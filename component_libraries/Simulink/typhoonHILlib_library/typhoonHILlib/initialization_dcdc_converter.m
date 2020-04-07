status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'ConvType');
    
    a_h = mask.getDialogControl('all_high_button');
    a_l = mask.getDialogControl('all_low_button');
    
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % Logic and Din panels start enabled
    log = mask.getDialogControl('logic_panel'); log.Enabled = 'on';
    di = mask.getDialogControl('di_panel'); di.Enabled = 'on';
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'Buck','Boost','Flyback'};
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'ConvType','Buck');
    end

    symm_param = mask.getParameter('Symmetrical');
    symm = get_param(thisBlock,'Symmetrical');
    symm_str = '';
    simweight = '1';
    logic_strs = {'s1_logic'};
    
    % Get the path to the correct pattern
    if strcmp('Boost', selected_type)
        if strcmp('on', symm)
            pat = 'typhoonPatterns/Symmetrical Boost';
            symm_str = 'Symmetrical ';
            logic_strs = {'s1_logic' 's2_logic'};
        else
            pat = 'typhoonPatterns/Boost';
        end
    elseif strcmp('Buck', selected_type)
        pat = 'typhoonPatterns/Buck';
    elseif strcmp('Flyback', selected_type)
        pat = 'typhoonPatterns/Flyback';
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
    
    
    
         
    % Setup logic blocks
    set_gate_logic(thisBlock, logic_strs);
    
    % Description update
    
    comp_string = [symm_str selected_type ' Converter'];
    comp_title = mask.getDialogControl('DescTitle');
    comp_title.Prompt = comp_string;
    
    description_text = ['Active switches and diodes are modeled as ideal switches in HIL simulation.<br><br>Weight = ' simweight];
    mask.set('Description', description_text);
    DescTitle.Visible = 'off';
    
    if pat_changed
        % Restore block position and size
        set_param(thisBlock,'Position', saved_pos);
    end
end
