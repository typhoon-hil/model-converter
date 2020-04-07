status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')
    
    mask_typ_ = Simulink.Mask.get(gcb);
    selected_type_typ_ = get_param(gcb, 'LineType');

    toggle_init_typ_ = mask_typ_.getParameter('toggle_init');
    toggle_init_typ_.Value = 'off'; 

    unit_sys_typ_ = get_param(gcb, 'unit_sys');
    last_unit_sys_param_typ_ = mask_typ_.getParameter('last_unit_sys');

    % Panels
    line_berg_panel_typ_ = mask_typ_.getDialogControl('LineParamsBergeron');
    line_berg_panel_typ_.Visible = 'off';
    line_rl_panel_typ_ = mask_typ_.getDialogControl('LineParamsRL');
    line_rl_panel_typ_.Visible = 'off';
    line_picoup_panel_typ_ = mask_typ_.getDialogControl('LineParamsPICoup');
    line_picoup_panel_typ_.Visible = 'off';

    % Line Parameters
    num_phases_param_typ_ = mask_typ_.getParameter('NumPhases');
    underground_param_typ_ = mask_typ_.getParameter('underground');
    underground_param_typ_.Visible = 'off';
    sequence_param_typ_ = mask_typ_.getParameter('sequence');
    sequence_param_typ_.Visible = 'off';
    r_picoup_mat_typ_ = mask_typ_.getParameter('r_picoup_mat');
    r_picoup_mat_typ_.Visible = 'off';
    r_picoup_seq_typ_ = mask_typ_.getParameter('r_picoup_seq');
    r_picoup_seq_typ_.Visible = 'off';
    r_picoup_mat_unit_typ_ = mask_typ_.getDialogControl('r_picoup_mat_unit');
    r_picoup_mat_unit_typ_.Visible = 'off';
    r_picoup_seq_unit_typ_ = mask_typ_.getDialogControl('r_picoup_seq_unit');
    r_picoup_seq_unit_typ_.Visible = 'off';
    l_picoup_mat_typ_ = mask_typ_.getParameter('l_picoup_mat');
    l_picoup_mat_typ_.Visible = 'off';
    l_picoup_seq_typ_ = mask_typ_.getParameter('l_picoup_seq');
    l_picoup_seq_typ_.Visible = 'off';
    l_picoup_mat_unit_typ_ = mask_typ_.getDialogControl('l_picoup_mat_unit');
    l_picoup_mat_unit_typ_.Visible = 'off';
    l_picoup_seq_unit_typ_ = mask_typ_.getDialogControl('l_picoup_seq_unit');
    l_picoup_seq_unit_typ_.Visible = 'off';
    c_picoup_mat_typ_ = mask_typ_.getParameter('c_picoup_mat');
    c_picoup_mat_typ_.Visible = 'off';
    c_picoup_seq_typ_ = mask_typ_.getParameter('c_picoup_seq');
    c_picoup_seq_typ_.Visible = 'off';
    c_picoup_mat_unit_typ_ = mask_typ_.getDialogControl('c_picoup_mat_unit');
    c_picoup_mat_unit_typ_.Visible = 'off';
    c_picoup_seq_unit_typ_ = mask_typ_.getDialogControl('c_picoup_seq_unit');
    c_picoup_seq_unit_typ_.Visible = 'off';
    rg_berg_typ_ = mask_typ_.getParameter('rg_berg');
    rg_berg_typ_.Visible = 'off';
    rg_berg_unit_typ_ = mask_typ_.getDialogControl('rg_berg_unit');
    rg_berg_unit_typ_.Visible = 'off';
    mc_berg_typ_ = mask_typ_.getParameter('mc_berg');
    mc_berg_typ_.Visible = 'off';
    mc_berg_unit_typ_ = mask_typ_.getDialogControl('mc_berg_unit');
    mc_berg_unit_typ_.Visible = 'off';

    switch selected_type_typ_
        case 'PI Section'
            line_picoup_panel_typ_.Visible = 'on';
            underground_param_typ_.Visible = 'on';
            underground_typ_ = get_param(gcb, 'underground');
            if strcmp(underground_typ_, 'on')
                num_phases_param_typ_.TypeOptions = {'1' '2' '3'};
            else
                num_phases_param_typ_.TypeOptions = {'2' '3' '4'};
            end
            num_phases_typ_ = get_param(gcb, 'NumPhases');
            if strcmp(num_phases_typ_, '3')
                sequence_param_typ_.Visible = 'on';
                sequence_typ_ = get_param(gcb, 'sequence');
                if strcmp(sequence_typ_, 'on')
                    r_picoup_seq_typ_.Visible = 'on';
                    r_picoup_seq_unit_typ_.Visible = 'on';
                    l_picoup_seq_typ_.Visible = 'on';
                    l_picoup_seq_unit_typ_.Visible = 'on';
                    c_picoup_seq_typ_.Visible = 'on';
                    c_picoup_seq_unit_typ_.Visible = 'on';
                else
                    r_picoup_mat_typ_.Visible = 'on';
                    r_picoup_mat_unit_typ_.Visible = 'on';
                    l_picoup_mat_typ_.Visible = 'on';
                    l_picoup_mat_unit_typ_.Visible = 'on';
                    c_picoup_mat_typ_.Visible = 'on';
                    c_picoup_mat_unit_typ_.Visible = 'on';
                end
            else
                r_picoup_mat_typ_.Visible = 'on';
                r_picoup_mat_unit_typ_.Visible = 'on';
                l_picoup_mat_typ_.Visible = 'on';
                l_picoup_mat_unit_typ_.Visible = 'on';
                c_picoup_mat_typ_.Visible = 'on';
                c_picoup_mat_unit_typ_.Visible = 'on';  
            end


        case 'RL Section'
            line_rl_panel_typ_.Visible = 'on';
            num_phases_param_typ_.TypeOptions = {'1' '2' '3' '4' '5'};
        case 'Coupled RL'
            line_picoup_panel_typ_.Visible = 'on';
            underground_param_typ_.Visible = 'on';
            underground_typ_ = get_param(gcb, 'underground');
            if strcmp(underground_typ_, 'on')
                num_phases_param_typ_.TypeOptions = {'1' '2' '3'};
            else
                num_phases_param_typ_.TypeOptions = {'2' '3' '4'};
            end
            num_phases_typ_ = get_param(gcb, 'NumPhases');
            if strcmp(num_phases_typ_, '3')
                sequence_param_typ_.Visible = 'on';
                sequence_typ_ = get_param(gcb, 'sequence');
                if strcmp(sequence_typ_, 'on')
                    r_picoup_seq_typ_.Visible = 'on';
                    r_picoup_seq_unit_typ_.Visible = 'on';
                    l_picoup_seq_typ_.Visible = 'on';
                    l_picoup_seq_unit_typ_.Visible = 'on';
                else
                    r_picoup_mat_typ_.Visible = 'on';
                    r_picoup_mat_unit_typ_.Visible = 'on';
                    l_picoup_mat_typ_.Visible = 'on';
                    l_picoup_mat_unit_typ_.Visible = 'on';
                end
            else
                r_picoup_mat_typ_.Visible = 'on';
                r_picoup_mat_unit_typ_.Visible = 'on';
                l_picoup_mat_typ_.Visible = 'on';
                l_picoup_mat_unit_typ_.Visible = 'on';
            end

        case 'Bergeron'
            line_berg_panel_typ_.Visible = 'on';
            num_phases_param_typ_.TypeOptions = {'3'};
            num_phases_typ_ = get_param(gcb, 'NumPhases');
            if strcmp(num_phases_typ_, '3')
                rg_berg_typ_.Visible = 'on';
                rg_berg_unit_typ_.Visible = 'on';
                mc_berg_typ_.Visible = 'on';
                mc_berg_unit_typ_.Visible = 'on';
            end

    end

    toggle_init_typ_.Value = 'on'; 

    clear c_picoup_mat_typ_         line_picoup_panel_typ_    r_picoup_seq_unit_typ_    
    clear c_picoup_mat_unit_typ_    line_rl_panel_typ_        rg_berg_typ_              
    clear c_picoup_seq_typ_         mask_typ_                 rg_berg_unit_typ_         
    clear c_picoup_seq_unit_typ_    mc_berg_typ_              selected_type_typ_        
    clear l_picoup_mat_typ_         mc_berg_unit_typ_         sequence_param_typ_       
    clear l_picoup_mat_unit_typ_    num_phases_param_typ_     toggle_init_typ_          
    clear l_picoup_seq_typ_         num_phases_typ_           underground_param_typ_    
    clear l_picoup_seq_unit_typ_    r_picoup_mat_typ_         underground_typ_          
    clear last_unit_sys_param_typ_  r_picoup_mat_unit_typ_    unit_sys_typ_             
    clear line_berg_panel_typ_      r_picoup_seq_typ_         sequence_typ_
    
end

clear status_typ_