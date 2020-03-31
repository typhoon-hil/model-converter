status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'LegType');
    
    % Logic, Din and Measurement panels start enabled
    log = mask.getDialogControl('logic_panel'); log.Enabled = 'on';
    di = mask.getDialogControl('di_panel'); di.Enabled = 'on';
    meas = mask.getDialogControl('meas_panel'); meas.Enabled = 'on';
    
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(thisBlock);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'Diode','IGBT','NPC','Antiparallel Thyristor','Flying Capacitor'};

    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'LegType','Diode');
    end
    
    extra_str = '';

    % Get the path to the correct pattern
    if strcmp('Diode', selected_type)
        simweight = '1';
        pat = 'typhoonPatterns/Diode Leg';
        
    %%%%%%%%%%%%%%%%%
    elseif strcmp('IGBT', selected_type)
        simweight = '1';
        pat = 'typhoonPatterns/IGBT Leg';
        
    %%%%%%%%%%%%%%%%%
    elseif strcmp('NPC', selected_type)

        simweight = '1';
        ttype = get_param(thisBlock,'Ttype');
        if strcmp('on', ttype)
            extra_str = 'T-Type ';
            pat = 'typhoonPatterns/NPC T-type Leg';
        else
            pat = 'typhoonPatterns/NPC Leg';
        end
        
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Antiparallel Thyristor', selected_type)
        simweight = '1';
        pat = 'typhoonPatterns/Antiparallel Thyristor Leg';
        
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Flying Capacitor', selected_type)

        % Check for comboBox invalid entries. Reset to Three-level.
        valid_combo = {'Three-level','Four-level','Five-level','Seven-level','Nine-level'};
        if ~any(strcmp(valid_combo, get_param(thisBlock,'FCLevels')))
            set_param(thisBlock,'FCLevels','Three-level');
        end
        
        % Choose pattern based on number of levels
        fclevels = get_param(thisBlock,'FCLevels');
        extra_str = [fclevels ' '];
        
        if strcmp('Three-level', fclevels)
            simweight = '1';
            pat = 'typhoonPatterns/FC Leg (3-level)';
        elseif strcmp('Four-level', fclevels)
            simweight = '2';
            pat = 'typhoonPatterns/FC Leg (4-level)';
        elseif strcmp('Five-level', fclevels)
            simweight = '2';
            pat = 'typhoonPatterns/FC Leg (5-level)';
        elseif strcmp('Seven-level', fclevels)
            simweight = '3';
            pat = 'typhoonPatterns/FC Leg (7-level)';
        elseif strcmp('Nine-level', fclevels)
            simweight = '3';
            pat = 'typhoonPatterns/FC Leg (9-level)';
        end
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
    
    % Create vectors with handlers to parameters that may be hidden
    logic_vec = []; i_meas_vec = []; v_meas_vec = [];
    i_meas_dctrl = []; v_meas_dctrl = []; di_vec = [];
    sw_vec = [];
    
    logic_strs = {  's1_logic' 's2_logic' 's3_logic' 's4_logic' 's5_logic' 's6_logic'...
                    's7_logic' 's8_logic' 's9_logic' 's10_logic' 's11_logic' 's12_logic'...
                    's13_logic' 's14_logic' 's15_logic' 's16_logic'};
                
    i_meas_strs = { 'i_s1' 'i_s2' 'i_s3' 'i_s4' 'i_s5' 'i_s6'...
                    'i_s7' 'i_s8' 'i_s9' 'i_s10' 'i_s11' 'i_s12'...
                    'i_s13' 'i_s14' 'i_s15' 'i_s16'};
                
    v_meas_strs = { 'v_s1' 'v_s2' 'v_s3' 'v_s4' 'v_s5' 'v_s6'...
                    'v_s7' 'v_s8' 'v_s9' 'v_s10' 'v_s11' 'v_s12'...
                    'v_s13' 'v_s14' 'v_s15' 'v_s16'};
                
    di_strs = { 'di_s1' 'di_s2' 'di_s3' 'di_s4' 'di_s5' 'di_s6'...
                'di_s7' 'di_s8' 'di_s9' 'di_s10' 'di_s11' 'di_s12'...
                'di_s13' 'di_s14' 'di_s15' 'di_s16'};
            
    sw_strs = { 's1' 's2' 's3' 's4' 's5' 's6'...
                's7' 's8' 's9' 's10' 's11' 's12'...
                's13' 's14' 's15' 's16'};

    for i=1:16
        logic_vec = [logic_vec, mask.getParameter(logic_strs{i})];
        i_meas_vec = [i_meas_vec, mask.getParameter(i_meas_strs{i})];
        i_meas_dctrl = [i_meas_dctrl, mask.getDialogControl(i_meas_strs{i})];
        v_meas_vec = [v_meas_vec, mask.getParameter(v_meas_strs{i})];
        v_meas_dctrl = [v_meas_dctrl, mask.getDialogControl(v_meas_strs{i})];
        di_vec = [di_vec, mask.getParameter(di_strs{i})];
        sw_vec = [sw_vec, mask.getDialogControl(sw_strs{i})];
    end
    
    % Parameter visibility and prompts 
    switch selected_type

        case 'Diode'
            prompts = {'D1', 'D2'};
            
        case 'IGBT'
            prompts = {'S1', 'S2'};
            
        case 'Antiparallel Thyristor'
            prompts = {'T1', 'T2'};
            
        case 'NPC'
            if strcmp('on', ttype)
                prompts = {'S1', 'S2', 'S3', 'S4'};
            else
                prompts = {'S1', 'S2', 'S3', 'S4', 'D1', 'D2'};
            end
                   
        case 'Flying Capacitor'
            fc_levels = get_param(thisBlock, 'FCLevels');
            switch fc_levels
                case 'Three-level'
                    prompts = {'S1', 'S2', 'S3', 'S4'};
                case 'Four-level'
                    prompts = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6'};
                case 'Five-level'
                    prompts = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'};
                case 'Seven-level'
                    prompts = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12'};
                case 'Nine-level'
                    prompts = { 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'...
                                'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16'};
            end
    end
    
    % Non T-Type NPC has two diodes
    if strcmp(selected_type, 'NPC')
        idxs = 1:4;
    else
        idxs = 1:size(prompts, 2);
    end
    
    % Toggle logic inverter block comment
    logic_params = logic_strs(idxs);
    if ~strcmp(selected_type,'Diode')
        set_gate_logic(thisBlock, logic_params);
    end
    
    % Setup measurement outputs
    setup_measurements(thisBlock, prompts, v_meas_strs, i_meas_strs);

    % Description update
    comp_string = [extra_str selected_type ' Leg'];
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
