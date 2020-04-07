status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')

    mask_typ_ = Simulink.Mask.get(gcb);

    % Panels
    log_typ_ = mask_typ_.getDialogControl('logic_panel'); log_typ_.Enabled = 'on';
    di_typ_ = mask_typ_.getDialogControl('di_panel'); di_typ_.Enabled = 'on';
    meas_typ_ = mask_typ_.getDialogControl('meas_panel'); meas_typ_.Enabled = 'on';
    ttype_param_typ_ = mask_typ_.getParameter('Ttype'); ttype_param_typ_.Visible = 'off';
    fclevels_param_typ_ = mask_typ_.getParameter('FCLevels'); fclevels_param_typ_.Visible = 'off';

    a_h_typ_ = mask_typ_.getDialogControl('all_high_button'); a_h_typ_.Enabled = 'on';
    a_l_typ_ = mask_typ_.getDialogControl('all_low_button'); a_l_typ_.Enabled = 'on';

    % Create vectors with handlers to parameters that may be hidden
    logic_vec_typ_ = []; i_meas_vec_typ_ = []; v_meas_vec_typ_ = [];
    i_meas_dctrl_typ_ = []; v_meas_dctrl_typ_ = []; di_vec_typ_ = [];
    sw_vec_typ_ = [];

    % Strings with the parameter names
    logic_strs_typ_ = {  's1_logic' 's2_logic' 's3_logic' 's4_logic' 's5_logic' 's6_logic'...
                        's7_logic' 's8_logic' 's9_logic' 's10_logic' 's11_logic' 's12_logic'...
                        's13_logic' 's14_logic' 's15_logic' 's16_logic'};

    i_meas_strs_typ_ = { 'i_s1' 'i_s2' 'i_s3' 'i_s4' 'i_s5' 'i_s6'...
                    'i_s7' 'i_s8' 'i_s9' 'i_s10' 'i_s11' 'i_s12'...
                    'i_s13' 'i_s14' 'i_s15' 'i_s16'};

    v_meas_strs_typ_ = { 'v_s1' 'v_s2' 'v_s3' 'v_s4' 'v_s5' 'v_s6'...
                    'v_s7' 'v_s8' 'v_s9' 'v_s10' 'v_s11' 'v_s12'...
                    'v_s13' 'v_s14' 'v_s15' 'v_s16'};

    di_strs_typ_ = { 'di_s1' 'di_s2' 'di_s3' 'di_s4' 'di_s5' 'di_s6'...
                'di_s7' 'di_s8' 'di_s9' 'di_s10' 'di_s11' 'di_s12'...
                'di_s13' 'di_s14' 'di_s15' 'di_s16'};

    sw_strs_typ_ = { 's1' 's2' 's3' 's4' 's5' 's6'...
                's7' 's8' 's9' 's10' 's11' 's12'...
                's13' 's14' 's15' 's16' 's17' 's18'};

    % Create vectors with all the parameters
    for i=1:16
        logic_vec_typ_ = [logic_vec_typ_, mask_typ_.getParameter(logic_strs_typ_{i})];
        i_meas_vec_typ_ = [i_meas_vec_typ_, mask_typ_.getParameter(i_meas_strs_typ_{i})];
        i_meas_dctrl_typ_ = [i_meas_dctrl_typ_, mask_typ_.getDialogControl(i_meas_strs_typ_{i})];
        v_meas_vec_typ_ = [v_meas_vec_typ_, mask_typ_.getParameter(v_meas_strs_typ_{i})];
        v_meas_dctrl_typ_ = [v_meas_dctrl_typ_, mask_typ_.getDialogControl(v_meas_strs_typ_{i})];
        di_vec_typ_ = [di_vec_typ_, mask_typ_.getParameter(di_strs_typ_{i})];
        sw_vec_typ_ = [sw_vec_typ_, mask_typ_.getDialogControl(sw_strs_typ_{i})];
    end

    % May be disabled by some components. Reset.
    arrayfun(@(x, y) set_enabled(x, 'on'), logic_vec_typ_(1:16));
    arrayfun(@(x, y) set_enabled(x, 'on'), di_vec_typ_(1:16));

    selected_type_typ_ = get_param(gcb,'LegType');
    % Parameter visibility and prompts 
    switch selected_type_typ_

        case 'Diode'
            prompts_typ_ = {'D1', 'D2'};
            log_typ_.Enabled = 'off';
            di_typ_.Enabled = 'off';

        case 'IGBT'
            prompts_typ_ = {'S1', 'S2'};

        case 'Antiparallel Thyristor'
            prompts_typ_ = {'T1', 'T2'};

        case 'NPC'
            ttype_param_typ_.Visible = 'on';
            ttype_typ_ = get_param(gcb, 'Ttype');
            if strcmp('on', ttype_typ_)
                prompts_typ_ = {'S1', 'S2', 'S3', 'S4'};
            else
                prompts_typ_ = {'S1', 'S2', 'S3', 'S4', 'D1', 'D2'};
            end

        case 'Flying Capacitor'
            fclevels_param_typ_.Visible = 'on';
            fc_levels_typ_ = get_param(gcb, 'FCLevels');
            switch fc_levels_typ_
                case 'Three-level'
                    prompts_typ_ = {'S1', 'S2', 'S3', 'S4'};
                case 'Four-level'
                    prompts_typ_ = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6'};
                case 'Five-level'
                    prompts_typ_ = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'};
                case 'Seven-level'
                    prompts_typ_ = {'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12'};
                case 'Nine-level'
                    prompts_typ_ = { 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'...
                                'S9', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16'};
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


    % Some elements are displayed only for measurement, they are not active switches
    switch selected_type_typ_

        case 'NPC'
            arrayfun(@(x, y) set_enabled(x, 'off'), logic_vec_typ_(5:6));
            arrayfun(@(x, y) set_enabled(x, 'off'), di_vec_typ_(5:6)); 

    end

    clear a_h_typ_             fclevels_param_typ_  idxs_typ_            meas_typ_            ttype_param_typ_     
    clear a_l_typ_             i                    log_typ_             prompts_typ_         ttype_typ_           
    clear di_strs_typ_         i_meas_dctrl_typ_    logic_strs_typ_      selected_type_typ_   v_meas_dctrl_typ_    
    clear di_typ_              i_meas_strs_typ_     logic_vec_typ_       sw_strs_typ_         v_meas_strs_typ_     
    clear di_vec_typ_          i_meas_vec_typ_      mask_typ_            sw_vec_typ_          v_meas_vec_typ_ 

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