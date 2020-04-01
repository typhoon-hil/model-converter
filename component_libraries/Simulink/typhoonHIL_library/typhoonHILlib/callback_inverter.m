status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')

    mask_typ_ = Simulink.Mask.get(gcb);

    % Panels
    log_typ_ = mask_typ_.getDialogControl('logic_panel'); log_typ_.Enabled = 'on';
    di_typ_ = mask_typ_.getDialogControl('di_panel'); di_typ_.Enabled = 'on';
    meas_typ_ = mask_typ_.getDialogControl('meas_panel'); meas_typ_.Enabled = 'on';
    fc_clamp_panel_typ_ = mask_typ_.getDialogControl('fc_clamp_panel'); fc_clamp_panel_typ_.Visible = 'off';

    tp_par_typ_ = mask_typ_.getParameter('ThreePhase'); tp_par_typ_.Enabled = 'off';
    a_h_typ_ = mask_typ_.getDialogControl('all_high_button'); a_h_typ_.Enabled = 'on';
    a_l_typ_ = mask_typ_.getDialogControl('all_low_button'); a_l_typ_.Enabled = 'on';

    % Create vectors with handlers to parameters that may be hidden
    logic_vec_typ_ = []; i_meas_vec_typ_ = []; v_meas_vec_typ_ = [];
    i_meas_dctrl_typ_ = []; v_meas_dctrl_typ_ = []; di_vec_typ_ = [];
    sw_vec_typ_ = [];

    % Strings with the parameter names
    logic_strs_typ_ = {  'sa1_logic' 'sa2_logic' 'sa3_logic' 'sa4_logic' 'sa5_logic' 'sa6_logic'...
                        'sb1_logic' 'sb2_logic' 'sb3_logic' 'sb4_logic' 'sb5_logic' 'sb6_logic'...
                        'sc1_logic' 'sc2_logic' 'sc3_logic' 'sc4_logic' 'sc5_logic' 'sc6_logic'};

    i_meas_strs_typ_ = { 'i_sa1' 'i_sa2' 'i_sa3' 'i_sa4' 'i_sa5' 'i_sa6'...
                        'i_sb1' 'i_sb2' 'i_sb3' 'i_sb4' 'i_sb5' 'i_sb6'...
                        'i_sc1' 'i_sc2' 'i_sc3' 'i_sc4' 'i_sc5' 'i_sc6'};

    v_meas_strs_typ_ = { 'v_sa1' 'v_sa2' 'v_sa3' 'v_sa4' 'v_sa5' 'v_sa6'...
                        'v_sb1' 'v_sb2' 'v_sb3' 'v_sb4' 'v_sb5' 'v_sb6'...
                        'v_sc1' 'v_sc2' 'v_sc3' 'v_sc4' 'v_sc5' 'v_sc6' };

    di_strs_typ_ = { 'di_sa1' 'di_sa2' 'di_sa3' 'di_sa4' 'di_sa5' 'di_sa6'...
                    'di_sb1' 'di_sb2' 'di_sb3' 'di_sb4' 'di_sb5' 'di_sb6'...
                    'di_sc1' 'di_sc2' 'di_sc3' 'di_sc4' 'di_sc5' 'di_sc6'};

    sw_strs_typ_ = { 'sa1' 'sa2' 'sa3' 'sa4' 'sa5' 'sa6'...
                    'sb1' 'sb2' 'sb3' 'sb4' 'sb5' 'sb6'...
                    'sc1' 'sc2' 'sc3' 'sc4' 'sc5' 'sc6'};

    % Create vectors with all the parameters
    for i=1:18
        logic_vec_typ_ = [logic_vec_typ_, mask_typ_.getParameter(logic_strs_typ_{i})];
        i_meas_vec_typ_ = [i_meas_vec_typ_, mask_typ_.getParameter(i_meas_strs_typ_{i})];
        i_meas_dctrl_typ_ = [i_meas_dctrl_typ_, mask_typ_.getDialogControl(i_meas_strs_typ_{i})];
        v_meas_vec_typ_ = [v_meas_vec_typ_, mask_typ_.getParameter(v_meas_strs_typ_{i})];
        v_meas_dctrl_typ_ = [v_meas_dctrl_typ_, mask_typ_.getDialogControl(v_meas_strs_typ_{i})];
        di_vec_typ_ = [di_vec_typ_, mask_typ_.getParameter(di_strs_typ_{i})];
        sw_vec_typ_ = [sw_vec_typ_, mask_typ_.getDialogControl(sw_strs_typ_{i})];
    end

    % May be disabled by some components. Reset.
    arrayfun(@(x, y) set_enabled(x, 'on'), logic_vec_typ_(1:18));
    arrayfun(@(x, y) set_enabled(x, 'on'), di_vec_typ_(1:18));

    selected_type_typ_ = get_param(gcb,'InvType');
    % Parameter visibility and prompts 
    switch selected_type_typ_

        case 'VSI'
            tp_par_typ_.Enabled = 'on';
            three_phase_typ_ = get_param(gcb, 'ThreePhase');
            if strcmp('on', three_phase_typ_)
                prompts_typ_ = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
            else
                prompts_typ_ = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
            end       

        case 'NPC'
            prompts_typ_ = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                        'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                        'Sc1' 'Sc2' 'Sc3' 'Sc4'...
                        'Da1' 'Da2' 'Db1' 'Db2' 'Dc1' 'Dc2'};

        case 'T-Type'
            prompts_typ_ = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                        'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                        'Sc1' 'Sc2' 'Sc3' 'Sc4'};

        case 'ANPC'
            prompts_typ_ = { 'Sa1' 'Sa2' 'Sa3' 'Sa4' 'Sa5' 'Sa6'...
                        'Sb1' 'Sb2' 'Sb3' 'Sb4' 'Sb5' 'Sb6'...
                        'Sc1' 'Sc2' 'Sc3' 'Sc4' 'Sc5' 'Sc6'};

        case 'Flying-Capacitor (3L)'
            fc_clamp_panel_typ_.Visible = 'on';
            prompts_typ_ = { 'Sa1' 'Sa2' 'Sa3' 'Sa4'...
                        'Sb1' 'Sb2' 'Sb3' 'Sb4'...
                        'Sc1' 'Sc2' 'Sc3' 'Sc4'...
                        'Ca' 'Cb' 'Cc'};

        case 'CSI (2L)'
            prompts_typ_ = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};

        case 'H5 (2L)'
            prompts_typ_ = { 'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'S5'};

        case 'H6'
            prompts_typ_ = { 'S1' 'S2' 'S3' 'S4' 'S5' 'S6' 'D1' 'D2'};

        case 'H6_5'
            prompts_typ_ = { 'S1' 'S2' 'S3' 'S4' 'S5' 'S6' 'D'};

        case 'Asymmetric'
            % To be implemented

    end

    if exist('prompts_typ_')
        % Prompts and tooltips
        idxs_typ_ = 1:size(prompts_typ_, 2);
        arrayfun(@(x,y) set_prompt(x, prompts_typ_{y}), sw_vec_typ_(idxs_typ_), idxs_typ_);
        arrayfun(@(x,y) set_tooltip(x, ['i_' prompts_typ_{y}]), i_meas_dctrl_typ_(idxs_typ_), idxs_typ_);
        arrayfun(@(x,y) set_tooltip(x, ['v_' prompts_typ_{y}]), v_meas_dctrl_typ_(idxs_typ_), idxs_typ_);
        % Visibility
        arrayfun(@(x) set_visibility(x, 'on'), logic_vec_typ_(1:size(prompts_typ_,2)));
        arrayfun(@(x) set_visibility(x, 'off'), logic_vec_typ_(size(prompts_typ_,2)+1:end));
        arrayfun(@(x) set_visibility(x, 'on'), i_meas_vec_typ_(1:size(prompts_typ_,2)));
        arrayfun(@(x) set_visibility(x, 'off'), i_meas_vec_typ_(size(prompts_typ_,2)+1:end));
        arrayfun(@(x) set_visibility(x, 'on'), v_meas_vec_typ_(1:size(prompts_typ_,2)));
        arrayfun(@(x) set_visibility(x, 'off'), v_meas_vec_typ_(size(prompts_typ_,2)+1:end));
        arrayfun(@(x) set_visibility(x, 'on'), di_vec_typ_(1:size(prompts_typ_,2)));
        arrayfun(@(x) set_visibility(x, 'off'), di_vec_typ_(size(prompts_typ_,2)+1:end));
        arrayfun(@(x) set_visibility(x, 'on'), sw_vec_typ_(1:size(prompts_typ_,2)));
        arrayfun(@(x) set_visibility(x, 'off'), sw_vec_typ_(size(prompts_typ_,2)+1:end));
    end


    % Some elements are displayed only for measurement, they are not active switches
    switch selected_type_typ_

        case 'NPC'
            arrayfun(@(x, y) set_enabled(x, 'off'), logic_vec_typ_(13:18));
            arrayfun(@(x, y) set_enabled(x, 'off'), di_vec_typ_(13:18)); 
        case 'Flying-Capacitor (3L)'
            arrayfun(@(x, y) set_enabled(x, 'off'), logic_vec_typ_(13:15));
            arrayfun(@(x, y) set_enabled(x, 'off'), di_vec_typ_(13:15)); 
        case 'H6'
            arrayfun(@(x, y) set_enabled(x, 'off'), logic_vec_typ_(7:8));
            arrayfun(@(x, y) set_enabled(x, 'off'), di_vec_typ_(7:8)); 
        case 'H6_5'
            arrayfun(@(x, y) set_enabled(x, 'off'), logic_vec_typ_(7));
            arrayfun(@(x, y) set_enabled(x, 'off'), di_vec_typ_(7)); 

    end

    clear a_h_typ_            i                   log_typ_            prompts_typ_        tp_par_typ_         
    clear a_l_typ_            i_meas_dctrl_typ_   logic_strs_typ_     selected_type_typ_  v_meas_dctrl_typ_   
    clear di_strs_typ_        i_meas_strs_typ_    logic_vec_typ_      sw_strs_typ_        v_meas_strs_typ_    
    clear di_typ_             i_meas_vec_typ_     mask_typ_           sw_vec_typ_         v_meas_vec_typ_     
    clear di_vec_typ_         idxs_typ_           meas_typ_           three_phase_typ_    fc_clamp_panel_typ_

end

clear status_typ_

function set_tooltip(dialogctrl, prompt)
    % tooltip = 'string'
    dialogctrl.Tooltip = prompt;
end

function set_enabled(param, status)
    % status = 'on', 'off'
    param.Enabled = status;
end