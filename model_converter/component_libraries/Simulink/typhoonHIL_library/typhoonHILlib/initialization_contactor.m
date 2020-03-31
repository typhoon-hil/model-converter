status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'ContType');
        
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {   'Single Pole Single Throw','Single Pole Double Throw','Double Pole Single Throw'...
                        'Double Pole Double Throw','Triple Pole Single Throw','Triple Pole Double Throw'};
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'ContType','Single Pole Single Throw');
    end

    switch selected_type
        case 'Single Pole Single Throw'
            pat = 'typhoonPatterns/SPST Contactor';
        case 'Single Pole Double Throw'
            pat = 'typhoonPatterns/SPDT Contactor';
        case 'Double Pole Single Throw'
            pat = 'typhoonPatterns/DPST Contactor';
        case 'Double Pole Double Throw'
            pat = 'typhoonPatterns/DPDT Contactor';
        case 'Triple Pole Single Throw'
            pat = 'typhoonPatterns/TPST Contactor';
        case 'Triple Pole Double Throw'
            pat = 'typhoonPatterns/TPDT Contactor';       
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

    di_1 = mask.getParameter('di_1'); di_2 = mask.getParameter('di_2'); 
    s1_logic = mask.getParameter('s1_logic'); s2_logic = mask.getParameter('s2_logic');
    s1 = mask.getDialogControl('s1'); s2 = mask.getDialogControl('s2'); 
    
    logic_strs = {'s1_logic'};
    
    % Setup logic blocks
    set_gate_logic(thisBlock, logic_strs);
    
    init_state = get_param(thisBlock, 'init_state');
    if strcmp(init_state, 'On / S1')
        set_param(thisBlock, 's0', '1');
    else
        set_param(thisBlock, 's0', '0');
    end
    
    % Description update
    comp_string = '%<ContType> Contactor';
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
end
