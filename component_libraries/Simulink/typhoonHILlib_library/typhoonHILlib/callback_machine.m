status_typ_ = get_param(bdroot, 'SimulationStatus');

if strcmp(status_typ_, 'stopped')

    mask_typ_ = Simulink.Mask.get(gcb);

    %% Parameter values
    selected_type_typ_ = get_param(gcb,'MachineType');
    selected_pmsm_rotor_typ_ = get_param(gcb,'RotorType_PMSM');
    selected_ind_rotor_typ_ = get_param(gcb,'RotorType_Ind');
    vbr_typ_ = get_param(gcb,'vbr');
    sp_ind_typ_ = get_param(gcb,'sp_ind');

    %% Parameters and units
    rotor_type_pmsm_typ_ = mask_typ_.getParameter('RotorType_PMSM');
    rotor_type_pmsm_typ_.Visible = 'off';
    rotor_type_ind_typ_ = mask_typ_.getParameter('RotorType_Ind');
    rotor_type_ind_typ_.Visible = 'off';
    stator_snb_typ_ = mask_typ_.getParameter('Rsnb_stator');
    stator_snb_typ_.Visible = 'off';
    stator_snb_unit_typ_ = mask_typ_.getDialogControl('Rsnb_stator_unit');
    stator_snb_unit_typ_.Visible = 'off';
    rotor_snb_typ_ = mask_typ_.getParameter('Rsnb_rotor');
    rotor_snb_typ_.Visible = 'off';
    rotor_snb_unit_typ_ = mask_typ_.getDialogControl('Rsnb_rotor_unit');
    rotor_snb_unit_typ_.Visible = 'off';
    vbr_param_typ_ = mask_typ_.getParameter('vbr');
    vbr_param_typ_.Visible = 'off';
    stardelta_typ_ = mask_typ_.getParameter('stardelta');
    stardelta_typ_.Visible = 'off';

    % Mechanical properties
    pms_typ_ = mask_typ_.getParameter('pms');
    pms_typ_.Visible = 'on';
    pms_unit_typ_ = mask_typ_.getDialogControl('pms_unit');
    pms_unit_typ_.Visible = 'on';
    stardelta_typ_ = mask_typ_.getParameter('stardelta');
    stardelta_typ_.Visible = 'off';
    w_disc_typ_ = mask_typ_.getParameter('w_disc');
    w_disc_typ_.Visible = 'off';
    w_disc_unit_typ_ = mask_typ_.getDialogControl('w_disc_unit');
    w_disc_unit_typ_.Visible = 'off';
    % Electrical properties
        % PMSM
    Ld_typ_ = mask_typ_.getParameter('Ld_pmsm');
    Ld_unit_typ_ = mask_typ_.getDialogControl('Ld_pmsm_unit');
    Lq_typ_ = mask_typ_.getParameter('Lq_pmsm');
    Lq_unit_typ_ = mask_typ_.getDialogControl('Lq_pmsm_unit');
    Lms_typ_ = mask_typ_.getParameter('Lms_pmsm');
    Lms_unit_typ_ = mask_typ_.getDialogControl('Lms_pmsm_unit');
    elec_pars_cyl_pmsm = [Lms_typ_];
    elec_pars_cyl_pmsm.Visible = 'off';
    elec_units_cyl_pmsm = [Lms_unit_typ_];
    elec_units_cyl_pmsm.Visible = 'off'; 
    elec_pars_salient_pmsm = [Ld_typ_ Lq_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_pars_salient_pmsm);
    elec_units_salient_pmsm = [Ld_unit_typ_ Lq_unit_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_units_salient_pmsm);
        % Induction Machine
    rr_ind_typ_ = mask_typ_.getParameter('Rr_ind');
    rr_ind_unit_typ_ = mask_typ_.getDialogControl('Rr_ind_unit');
    rrc_ind_typ_ = mask_typ_.getParameter('Rrc_ind');
    rrc_ind_unit_typ_ = mask_typ_.getDialogControl('Rrc_ind_unit');
    rr1_ind_typ_ = mask_typ_.getParameter('Rr1_ind');
    rr1_ind_unit_typ_ = mask_typ_.getDialogControl('Rr1_ind_unit');
    rr2_ind_typ_ = mask_typ_.getParameter('Rr2_ind');
    rr2_ind_unit_typ_ = mask_typ_.getDialogControl('Rr2_ind_unit');
    llr_ind_typ_ = mask_typ_.getParameter('Llr_ind');
    llr_ind_unit_typ_ = mask_typ_.getDialogControl('Llr_ind_unit');
    llr1_ind_typ_ = mask_typ_.getParameter('Llr1_ind');
    llr1_ind_unit_typ_ = mask_typ_.getDialogControl('Llr1_ind_unit');
    llr2_ind_typ_ = mask_typ_.getParameter('Llr2_ind');
    llr2_ind_unit_typ_ = mask_typ_.getDialogControl('Llr2_ind_unit');
    lmr_ind_typ_ = mask_typ_.getParameter('Lmr_ind');
    lmr_ind_unit_typ_ = mask_typ_.getDialogControl('Lmr_ind_unit');
    elec_pars_ind_squirrel = [rr_ind_typ_ llr_ind_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_pars_ind_squirrel);
    elec_units_ind_squirrel = [rr_ind_unit_typ_ llr_ind_unit_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_units_ind_squirrel);
    elec_pars_ind_double = [rrc_ind_typ_ rr1_ind_typ_ rr2_ind_typ_ ...
                            llr1_ind_typ_ llr2_ind_typ_ lmr_ind_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_pars_ind_double);
    elec_units_ind_double = [rrc_ind_unit_typ_ rr1_ind_unit_typ_ rr2_ind_unit_typ_ ...
                             llr1_ind_unit_typ_ llr2_ind_unit_typ_ lmr_ind_unit_typ_];
    arrayfun(@(x) set_visibility(x,'off'), elec_units_ind_double);

    %% Panels
    sp_ind_panel_typ_ = mask_typ_.getDialogControl('sp_ind_panel');
    sp_ind_panel_typ_.Visible = 'off';
    advanced_typ_ = mask_typ_.getDialogControl('advanced');
    advanced_typ_.Visible = 'off';
    snubber_typ_ = mask_typ_.getDialogControl('snubber');
    snubber_typ_.Visible = 'off';
        % Electrical properties panels
    electrical_pmsm_typ_ = mask_typ_.getDialogControl('electrical_pmsm');
    electrical_pmsm_typ_.Visible = 'off';
    electrical_DC_typ_ = mask_typ_.getDialogControl('electrical_DC');
    electrical_DC_typ_.Visible = 'off';
    electrical_ind_typ_ = mask_typ_.getDialogControl('electrical_ind');
    electrical_ind_typ_.Visible = 'off';
    electrical_sp_ind_typ_ = mask_typ_.getDialogControl('electrical_sp_ind');
    electrical_sp_ind_typ_.Visible = 'off';

    %%
    if strcmp(selected_type_typ_, 'PMSM')
        %%
        electrical_pmsm_typ_.Visible = 'on';
        rotor_type_pmsm_typ_.Visible = 'on';
        pms_typ_.Visible = 'on';
        pms_unit_typ_.Visible = 'on';

        selected_pmsm_rotor_typ_ = get_param(gcb,'RotorType_PMSM');
        if strcmp(selected_pmsm_rotor_typ_, 'Salient Pole')
            arrayfun(@(x) set_visibility(x,'on'), elec_pars_salient_pmsm);
            stardelta_typ_.Visible = 'on';
            advanced_typ_.Visible = 'on';
            vbr_param_typ_.Visible = 'on';
        else
            arrayfun(@(x) set_visibility(x,'on'), elec_pars_cyl_pmsm);
        end
        %
        vbr_typ_ = get_param(gcb,'vbr');
        if strcmp(vbr_typ_, 'off')
            snubber_typ_.Visible = 'on';
            stator_snb_typ_.Visible = 'on';
            stator_snb_unit_typ_.Visible = 'on';
        end

    elseif strcmp(selected_type_typ_, 'Induction Machine')
        %%
        sp_ind_panel_typ_.Visible = 'on';
        sp_ind_typ_ = get_param(gcb,'sp_ind');
        if strcmp(sp_ind_typ_, 'on')
            electrical_sp_ind_typ_.Visible = 'on';
            w_disc_typ_.Visible = 'on';
            w_disc_unit_typ_.Visible = 'on';
        else
            electrical_ind_typ_.Visible = 'on';
            rotor_type_ind_typ_.Visible = 'on';

            selected_ind_rotor_typ_ = get_param(gcb,'RotorType_Ind');
            if strcmp(selected_ind_rotor_typ_, 'Squirrel Cage')
                arrayfun(@(x) set_visibility(x,'on'), elec_pars_ind_squirrel);
                vbr_param_typ_.Visible = 'on';
                vbr_typ_ = get_param(gcb,'vbr');
                if strcmp(vbr_typ_, 'on')
                    advanced_typ_.Visible = 'on';
                else
                    snubber_typ_.Visible = 'on';
                    stator_snb_typ_.Visible = 'on';
                    stator_snb_unit_typ_.Visible = 'on';
                end
            else
                arrayfun(@(x) set_visibility(x,'on'), elec_pars_ind_double);
                snubber_typ_.Visible = 'on';
                stator_snb_typ_.Visible = 'on';
                stator_snb_unit_typ_.Visible = 'on';
            end
        end

    elseif strcmp(selected_type_typ_, 'DC Machine')
        %%
        pms_typ_.Visible = 'off';
        pms_unit_typ_.Visible = 'off';
        electrical_DC_typ_.Visible = 'on';
        snubber_typ_.Visible = 'on';
        rotor_snb_typ_.Visible = 'on';
        rotor_snb_unit_typ_.Visible = 'on';
        stator_snb_typ_.Visible = 'on';
        stator_snb_unit_typ_.Visible = 'on';

    end             

    clear Ld_typ_                   elec_units_ind_double     llr_ind_unit_typ_         rr2_ind_typ_              stardelta_typ_            
    clear Ld_unit_typ_              elec_units_ind_squirrel   lmr_ind_typ_              rr2_ind_unit_typ_         stator_snb_typ_           
    clear Lms_typ_                  elec_units_salient_pmsm   lmr_ind_unit_typ_         rr_ind_typ_               stator_snb_unit_typ_      
    clear Lms_unit_typ_             electrical_DC_typ_        mask_typ_                 rr_ind_unit_typ_          vbr_param_typ_            
    clear Lq_typ_                   electrical_ind_typ_       pms_typ_                  rrc_ind_typ_              vbr_typ_                  
    clear Lq_unit_typ_              electrical_pmsm_typ_      pms_unit_typ_             rrc_ind_unit_typ_         w_disc_typ_               
    clear advanced_typ_             electrical_sp_ind_typ_    rotor_snb_typ_            selected_ind_rotor_typ_   w_disc_unit_typ_          
    clear elec_pars_cyl_pmsm        llr1_ind_typ_             rotor_snb_unit_typ_       selected_pmsm_rotor_typ_  
    clear elec_pars_ind_double      llr1_ind_unit_typ_        rotor_type_ind_typ_       selected_type_typ_        
    clear elec_pars_ind_squirrel    llr2_ind_typ_             rotor_type_pmsm_typ_      snubber_typ_              
    clear elec_pars_salient_pmsm    llr2_ind_unit_typ_        rr1_ind_typ_              sp_ind_panel_typ_         
    clear elec_units_cyl_pmsm       llr_ind_typ_              rr1_ind_unit_typ_         sp_ind_typ_ 

end

clear status_typ_

