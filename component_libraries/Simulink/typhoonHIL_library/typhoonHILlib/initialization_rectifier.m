status = get_param(bdroot, 'SimulationStatus');
thisBlock = gcb;

% Check for a flag indicating the initialization should be ignored
ignore_init = ~strcmp(get_param(thisBlock,'toggle_init'),'on');

if strcmp(status, 'stopped')&~ignore_init&~strcmp(bdroot,'typhoonHILlib')
    disp('init_called')
    mask = Simulink.Mask.get(thisBlock);
    selected_type = get_param(thisBlock,'RecType');
    
    a_h = mask.getDialogControl('all_high_button');
    a_l = mask.getDialogControl('all_low_button');
    
    % Logic, Din and Measurement panels start enabled
    log = mask.getDialogControl('logic_panel'); log.Enabled = 'on';
    di = mask.getDialogControl('di_panel'); di.Enabled = 'on';
    meas = mask.getDialogControl('meas_panel'); meas.Enabled = 'on';
    
    % Draw icon
    [sizex, sizey, size_str] = get_blocksize(thisBlock);
    old_size = mask.getParameter('old_size');
    old_size.Value = size_str;
    
    % If the comboBox entry is invalid, force Diode
    valid_options = {'Diode','Thyristor','Vienna'};
    if ~any(strcmp(valid_options, selected_type))
        set_param(thisBlock,'RecType','Diode');
    end

    three_phase = get_param(thisBlock,'ThreePhase');
    % Get the path to the correct pattern
    if strcmp('Diode', selected_type)
        if strcmp('on', three_phase)
            pat = 'typhoonPatterns/Diode Rectifier (3-Phase)';
            phase_str = 'Three-Phase ';
            simweight = '3';
        else
            pat = 'typhoonPatterns/Diode Rectifier (1-Phase)';
            phase_str = 'Single-Phase ';
            simweight = '1';
        end
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Thyristor', selected_type)
        if strcmp('on', three_phase)
            pat = 'typhoonPatterns/Thyristor Rectifier (3-Phase)';
            phase_str = 'Three-Phase ';
            simweight = '3';
        else
            pat = 'typhoonPatterns/Thyristor Rectifier (1-Phase)';
            phase_str = 'Single-Phase ';
            simweight = '2';
        end
    %%%%%%%%%%%%%%%%%
    elseif strcmp('Vienna', selected_type)
        pat = 'typhoonPatterns/Vienna Rectifier';
        phase_str = '';
        simweight = '3';
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

    % Strings with the parameter names
    logic_strs = {'sa_top_logic' 'sa_bot_logic' 'sb_top_logic' 'sb_bot_logic' 'sc_top_logic' 'sc_bot_logic'};
    i_meas_strs = {'i_sa_top' 'i_sa_bot' 'i_sb_top' 'i_sb_bot' 'i_sc_top' 'i_sc_bot'};
    v_meas_strs = {'v_sa_top' 'v_sa_bot' 'v_sb_top' 'v_sb_bot' 'v_sc_top' 'v_sc_bot'};
    di_strs = {'di_sa_top' 'di_sa_bot' 'di_sb_top' 'di_sb_bot' 'di_sc_top' 'di_sc_bot'};
    sw_strs = {'txt1' 'txt2' 'txt3' 'txt4' 'txt5' 'txt6'};

    % Create vectors with all the parameters
    for i=1:6
        logic_vec = [logic_vec, mask.getParameter(logic_strs{i})];
        i_meas_vec = [i_meas_vec, mask.getParameter(i_meas_strs{i})];
        i_meas_dctrl = [i_meas_dctrl, mask.getDialogControl(i_meas_strs{i})];
        v_meas_vec = [v_meas_vec, mask.getParameter(v_meas_strs{i})];
        v_meas_dctrl = [v_meas_dctrl, mask.getDialogControl(v_meas_strs{i})];
        di_vec = [di_vec, mask.getParameter(di_strs{i})];
        sw_vec = [sw_vec, mask.getDialogControl(sw_strs{i})];
    end

    switch selected_type

        case 'Vienna'
         
            set_param(thisBlock, 'ThreePhase', 'on');
            prompts = {'Sa' 'Sb' 'Sc'};

        case 'Diode'
            a_h.Enabled = 'off';
            a_l.Enabled = 'off';
            di.Enabled = 'off';

            three_phase = get_param(thisBlock, 'ThreePhase');
            if strcmp('on', three_phase)
                prompts = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
            else
                prompts = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
            end

        case 'Thyristor'
            three_phase = get_param(thisBlock, 'ThreePhase');
           
            if strcmp('on', three_phase)
                prompts = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
            else
                prompts = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
            end

    end 

    idxs = 1:size(prompts, 2);    
        
    %Toggle logic inverter block comment
    logic_params = logic_strs(idxs);
    if ~strcmp(selected_type,'Diode')
        set_gate_logic(thisBlock, logic_params);
    end

    % Setup measurement outputs
    setup_measurements(thisBlock, prompts, v_meas_strs, i_meas_strs);

    % Description update
    comp_string = [phase_str selected_type ' Rectifier'];
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
