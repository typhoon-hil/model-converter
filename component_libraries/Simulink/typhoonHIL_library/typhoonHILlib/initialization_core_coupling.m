status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    is_tlm = get_param(thisBlock,'IsTLM');
    num_phases = get_param(thisBlock,'CouplingPhases');
        
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(gcb);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Single-Phase
    valid_options = {'Single-Phase', 'Three-Phase', 'Four-Phase', 'Five-Phase'};
                    
    if ~any(strcmp(valid_options, num_phases))
        set_param(thisBlock,'CouplingPhases','Single-Phase');
    end
    
    switch num_phases
        case 'Single-Phase'
            pat = 'typhoonPatterns/SP CC';
        case 'Three-Phase'
            pat = 'typhoonPatterns/TP CC';
        case 'Four-Phase'
            pat = 'typhoonPatterns/4P CC';
        case 'Five-Phase'
            pat = 'typhoonPatterns/5P CC';
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
    if strcmp(is_tlm,'on')
        comp_string = '%<CouplingPhases> TLM Core Coupling';
        %description_text = ['Transmission line based coupling element.<br><br>'...
        %                'Important note:<br>'...
        %                '- Use bilinear discretization method<br>'...
        %                '- Use explicit simulation step value, automatic option will result in error<br>'...
        %                '- Replace existing inductor with same value TLM inductive coupling<br>'...
        %                '- Replace existing capacitor with same value TLM capacitive coupling<br>'...
        %]
    else
        comp_string = '%<CouplingPhases> Core Coupling';
    end
    
    description_text = ['<br>' CouplingPhases ' Core Coupling<br>'];
    %comp_title = mask.getDialogControl('DescTitle');
    %comp_title.Prompt = comp_string;
   
    mask.set('Description', description_text);
    DescTitle.Visible = 'on';
    
    if pat_changed
        % Restore block position and size
        set_param(thisBlock,'Position', saved_pos);
    end
end

