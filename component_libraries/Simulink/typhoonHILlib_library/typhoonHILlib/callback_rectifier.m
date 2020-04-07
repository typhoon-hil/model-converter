status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')
    disp('callback called')
    mask_typ_ = Simulink.Mask.get(gcb);

    % Panels
    log_typ_ = mask_typ_.getDialogControl('logic_panel'); log_typ_.Enabled = 'on';
    di_typ_ = mask_typ_.getDialogControl('di_panel'); di_typ_.Enabled = 'on';
    meas_typ_ = mask_typ_.getDialogControl('meas_panel'); meas_typ_.Enabled = 'on';
    tp_par_typ_ = mask_typ_.getParameter('ThreePhase'); tp_par_typ_.Enabled = 'on';

    a_h_typ_ = mask_typ_.getDialogControl('all_high_button'); a_h_typ_.Enabled = 'on';
    a_l_typ_ = mask_typ_.getDialogControl('all_low_button'); a_l_typ_.Enabled = 'on';

    % Create vectors with handlers to parameters that may be hidden
    logic_vec_typ_ = []; i_meas_vec_typ_ = []; v_meas_vec_typ_ = [];
    i_meas_dctrl_typ_ = []; v_meas_dctrl_typ_ = []; di_vec_typ_ = [];
    sw_vec_typ_ = [];

    % Strings with the parameter names
    logic_strs_typ_ = {'sa_top_logic' 'sa_bot_logic' 'sb_top_logic' 'sb_bot_logic' 'sc_top_logic' 'sc_bot_logic'};
    i_meas_strs_typ_ = {'i_sa_top' 'i_sa_bot' 'i_sb_top' 'i_sb_bot' 'i_sc_top' 'i_sc_bot'};
    v_meas_strs_typ_ = {'v_sa_top' 'v_sa_bot' 'v_sb_top' 'v_sb_bot' 'v_sc_top' 'v_sc_bot'};
    di_strs_typ_ = {'di_sa_top' 'di_sa_bot' 'di_sb_top' 'di_sb_bot' 'di_sc_top' 'di_sc_bot'};
    sw_strs_typ_ = {'txt1' 'txt2' 'txt3' 'txt4' 'txt5' 'txt6'};
    % Create vectors with all the parameters
    for i=1:6
        logic_vec_typ_ = [logic_vec_typ_, mask_typ_.getParameter(logic_strs_typ_{i})];
        i_meas_vec_typ_ = [i_meas_vec_typ_, mask_typ_.getParameter(i_meas_strs_typ_{i})];
        i_meas_dctrl_typ_ = [i_meas_dctrl_typ_, mask_typ_.getDialogControl(i_meas_strs_typ_{i})];
        v_meas_vec_typ_ = [v_meas_vec_typ_, mask_typ_.getParameter(v_meas_strs_typ_{i})];
        v_meas_dctrl_typ_ = [v_meas_dctrl_typ_, mask_typ_.getDialogControl(v_meas_strs_typ_{i})];
        di_vec_typ_ = [di_vec_typ_, mask_typ_.getParameter(di_strs_typ_{i})];
        sw_vec_typ_ = [sw_vec_typ_, mask_typ_.getDialogControl(sw_strs_typ_{i})];
    end

    selected_type_typ_ = get_param(gcb,'RecType');

    switch selected_type_typ_

        case 'Vienna'

            tp_par_typ_.Enabled = 'off';
            prompts_typ_ = {'Sa' 'Sb' 'Sc'};

        case 'Diode'
            a_h_typ_.Enabled = 'off';
            a_l_typ_.Enabled = 'off';
            di_typ_.Enabled = 'off';
            log_typ_.Enabled = 'off';

            three_phase_typ_ = get_param(gcb, 'ThreePhase');
            if strcmp('on', three_phase_typ_)
                prompts_typ_ = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
            else
                prompts_typ_ = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
            end

        case 'Thyristor'
            three_phase_typ_ = get_param(gcb, 'ThreePhase');
            if strcmp('on', three_phase_typ_)
                prompts_typ_ = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot' 'Sc_top' 'Sc_bot'};
            else
                prompts_typ_ = {'Sa_top' 'Sa_bot' 'Sb_top' 'Sb_bot'};
            end

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

    clear a_h_typ_            i                   log_typ_            prompts_typ_        tp_par_typ_         
    clear a_l_typ_            i_meas_dctrl_typ_   logic_strs_typ_     selected_type_typ_  v_meas_dctrl_typ_   
    clear di_strs_typ_        i_meas_strs_typ_    logic_vec_typ_      sw_strs_typ_        v_meas_strs_typ_    
    clear di_typ_             i_meas_vec_typ_     mask_typ_           sw_vec_typ_         v_meas_vec_typ_     
    clear di_vec_typ_         idxs_typ_           meas_typ_           three_phase_typ_  

end

clear status_typ_

function set_tooltip(dialogctrl, prompt)
    % tooltip = 'string'
    dialogctrl.Tooltip = prompt;
end