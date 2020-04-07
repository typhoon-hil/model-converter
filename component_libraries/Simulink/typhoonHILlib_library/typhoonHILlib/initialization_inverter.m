status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'InvType');
    
    % Logic, Din and Measurement panels start enabled
    log = mask.getDialogControl('logic_panel'); log.Enabled = 'on';
    di = mask.getDialogControl('di_panel'); di.Enabled = 'on';
    meas = mask.getDialogControl('meas_panel'); meas.Enabled = 'on';
    
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(thisBlock);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'VSI','NPC','T-Type','ANPC','Asymmetric','Flying-Capacitor (3L)','CSI (2L)','H5 (2L)','H6','H6_5'};
    
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'InvType','VSI');
    end

    three_phase = get_param(thisBlock,'ThreePhase');
    % Get the path to the correct pattern
    if strcmp('VSI', selected_type)
        if strcmp('on', three_phase)
            pat = 'typhoonPatterns/VSI (3-Phase)';
            phase_str = 'Three-Phase ';
            simweight = '3';
        else
            pat = 'typhoonPatterns/VSI (1-Phase)';
            phase_str = 'Single-Phase ';
            simweight = '1';
        end
    %%%%%%%%%%%%%%%%%
    elseif strcmp('NPC', selected_type)
        pat = 'typhoonPatterns/NPC Inverter';
        phase_str = '';
        simweight = '3';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('T-Type', selected_type)
        pat = 'typhoonPatterns/T-Type Inverter';
        phase_str = '';
        simweight = '3';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('ANPC', selected_type)
        pat = 'typhoonPatterns/ANPC Inverter';
        phase_str = '';
        simweight = '3';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Asymmetric', selected_type)
        pat = 'typhoonPatterns/Asymmetric Inverter (3-Phase)';
        phase_str = '';
        simweight = '3';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Flying-Capacitor (3L)', selected_type)
        pat = 'typhoonPatterns/3L Flying Capacitor Inverter';
        phase_str = '';
        simweight = '3';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('CSI (2L)', selected_type)
        pat = 'typhoonPatterns/CSI (3-Phase)';
        phase_str = '';
        simweight = '2';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('H5 (2L)', selected_type)
        pat = 'typhoonPatterns/2L H5 Inverter';
        phase_str = '';
        simweight = ' ';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('H6', selected_type)
        pat = 'typhoonPatterns/H6 Inverter';
        phase_str = '';
        simweight = ' ';
    %%%%%%%%%%%%%%%%%
    elseif strcmp('H6_5', selected_type)
        pat = 'typhoonPatterns/H6_5 Inverter';
        phase_str = '';
        simweight = ' ';
    %%%%%%%%%%%%%%%%%
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
    
    logic_strs = {  'sa1_logic' 'sa2_logic' 'sa3_logic' 'sa4_logic' 'sa5_logic' 'sa6_logic'...
                    'sb1_logic' 'sb2_logic' 'sb3_logic' 'sb4_logic' 'sb5_logic' 'sb6_logic'...
                    'sc1_logic' 'sc2_logic' 'sc3_logic' 'sc4_logic' 'sc5_logic' 'sc6_logic'};
                
    i_meas_strs = { 'i_sa1' 'i_sa2' 'i_sa3' 'i_sa4' 'i_sa5' 'i_sa6'...
                    'i_sb1' 'i_sb2' 'i_sb3' 'i_sb4' 'i_sb5' 'i_sb6'...
                    'i_sc1' 'i_sc2' 'i_sc3' 'i_sc4' 'i_sc5' 'i_sc6'};
                
    v_meas_strs = { 'v_sa1' 'v_sa2' 'v_sa3' 'v_sa4' 'v_sa5' 'v_sa6'...
                    'v_sb1' 'v_sb2' 'v_sb3' 'v_sb4' 'v_sb5' 'v_sb6'...
                    'v_sc1' 'v_sc2' 'v_sc3' 'v_sc4' 'v_sc5' 'v_sc6' };
                
    di_strs = { 'di_sa1' 'di_sa2' 'di_sa3' 'di_sa4' 'di_sa5' 'di_sa6'...
                'di_sb1' 'di_sb2' 'di_sb3' 'di_sb4' 'di_sb5' 'di_sb6'...
                'di_sc1' 'di_sc2' 'di_sc3' 'di_sc4' 'di_sc5' 'di_sc6'};
            
    sw_strs = { 'sa1' 'sa2' 'sa3' 'sa4' 'sa5' 'sa6'...
                'sb1' 'sb2' 'sb3' 'sb4' 'sb5' 'sb6'...
                'sc1' 'sc2' 'sc3' 'sc4' 'sc5' 'sc6'};

    for i=1:18
        logic_vec = [logic_vec, mask.getParameter(logic_strs{i})];
        i_meas_vec = [i_meas_vec, mask.getParameter(i_meas_strs{i})];
        i_meas_dctrl = [i_meas_dctrl, mask.getDialogControl(i_meas_strs{i})];
        v_meas_vec = [v_meas_vec, mask.getParameter(v_meas_strs{i})];
        v_meas_dctrl = [v_meas_dctrl, mask.getDialogControl(v_meas_strs{i})];
        di_vec = [di_vec, mask.getParameter(di_strs{i})];
        sw_vec = [sw_vec, mask.getDialogControl(sw_strs{i})];
    end
    
    tp_par = mask.getParameter('ThreePhase');
    
    switch selected_type

    case 'VSI'
        tp_par.Enabled = 'on';
        three_phase = get_param(thisBlock, 'ThreePhase');
        if strcmp('on', three_phase)
            prompts = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
        else
            prompts = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
        end
        idxs = 1:size(prompts, 2); 

    case 'NPC'
        set_param(thisBlock,'ThreePhase','on');
        prompts = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                    'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                    'Sc1' 'Sc2' 'Sc3' 'Sc4'...
                    'Da1' 'Da2' 'Db1' 'Db2' 'Dc1' 'Dc2'};         
        idxs = 1:12; 

    case 'T-Type'
        set_param(thisBlock,'ThreePhase','on');
        prompts = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                    'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                    'Sc1' 'Sc2' 'Sc3' 'Sc4'};
        idxs = 1:size(prompts, 2); 

    case 'ANPC'
        set_param(thisBlock,'ThreePhase','on');
        prompts = { 'Sa1' 'Sa2' 'Sa3' 'Sa4' 'Sa5' 'Sa6'...
                    'Sb1' 'Sb2' 'Sb3' 'Sb4' 'Sb5' 'Sb6'...
                    'Sc1' 'Sc2' 'Sc3' 'Sc4' 'Sc5' 'Sc6'};
        idxs = 1:size(prompts, 2); 
        
    case 'Flying-Capacitor (3L)'
        set_param(thisBlock,'ThreePhase','on');
        prompts = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                    'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                    'Sc1' 'Sc2' 'Sc3' 'Sc4'...
                    'Ca' 'Cb' 'Cc'};
        idxs = 1:12; 
        
    case 'CSI (2L)'
        set_param(thisBlock,'ThreePhase','on');
        prompts = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
        idxs = 1:size(prompts, 2);
        
    case 'H5 (2L)'
        prompts = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'S5'};
        idxs = 1:size(prompts, 2);
        
    case 'H6'
        prompts = { 'S1' 'S2' 'S3' 'S4' 'S5' 'S6' 'D1' 'D2'};
        idxs = 1:6; 
        
    case 'H6_5'
        prompts = { 'S1' 'S2' 'S3' 'S4' 'S5' 'S6' 'D'};
        idxs = 1:6; 
        
    case 'Asymmetric'
        % To be implemented

    end
        
    %Toggle logic inverter block comment
    logic_params = logic_strs(idxs);
    if ~strcmp(selected_type,'Diode')
        set_gate_logic(thisBlock, logic_params);
    end

    %Setup measurement outputs
    setup_measurements(thisBlock, prompts, v_meas_strs, i_meas_strs);

    % Description update
    comp_string = [phase_str selected_type ' Inverter'];
    comp_title = mask.getDialogControl('DescTitle');
    comp_title.Prompt = comp_string;
    description_text = ['Active switches and diodes are modeled as ideal switches in HIL simulation.<br><br>Weight = ' simweight];
    mask.set('Description', description_text);
    DescTitle.Visible = 'off';
    
    % Restore block position and size    
    if pat_changed
        set_param(thisBlock,'Position', saved_pos);
    end
end
