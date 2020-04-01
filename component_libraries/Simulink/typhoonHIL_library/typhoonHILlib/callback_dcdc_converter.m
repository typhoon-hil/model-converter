mask_typ_ = Simulink.Mask.get(gcb);

status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')

    symm_param_typ_ = mask_typ_.getParameter('Symmetrical'); symm_param_typ_.Visible = 'off';
    transf_pars_typ_ = mask_typ_.getDialogControl('TransfParams'); transf_pars_typ_.Visible = 'off';
    
    s2_text_typ_ = mask_typ_.getDialogControl('s2'); s2_text_typ_.Visible = 'off';
    s2_logic_typ_ = mask_typ_.getParameter('s2_logic'); s2_logic_typ_.Visible = 'off';
    di_s2_typ_ = mask_typ_.getParameter('di_s2'); di_s2_typ_.Visible = 'off';
    
    % Get the converter currently selected in the ComboBox
    selected_type_typ_ = get_param(gcb,'ConvType');
    
    if strcmp('Boost', selected_type_typ_)
        symm_param_typ_.Visible = 'on';
        selected_symm_typ_ = get_param(gcb,'Symmetrical');
        if strcmp(selected_symm_typ_, 'on')
            s2_text_typ_.Visible = 'on';
            s2_logic_typ_.Visible = 'on';
            di_s2_typ_.Visible = 'on';
        end
    elseif strcmp('Flyback', selected_type_typ_)
        transf_pars_typ_.Visible = 'on';
    end

    
end

clear status_typ_