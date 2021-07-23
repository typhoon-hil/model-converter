mask_typ_ = Simulink.Mask.get(gcb);

input_dig_typ_ = mask_typ_.getParameter('addr_digital'); input_dig_typ_.Visible = 'off';
input_analog_typ_ = mask_typ_.getParameter('addr_analog'); input_analog_typ_.Visible = 'off';
invert_typ_ = mask_typ_.getParameter('invert'); invert_typ_.Visible = 'off';
min_typ_ = mask_typ_.getParameter('min'); min_typ_.Visible = 'off';
max_typ_ = mask_typ_.getParameter('max'); max_typ_.Visible = 'off';
def_value_typ_ = mask_typ_.getParameter('def_value'); def_value_typ_.Visible = 'off';

switch get_param(gcb, 'InputType')
    case 'Digital Input'
        input_dig_typ_.Visible = 'on';
        invert_typ_.Visible = 'on';
    case 'Analog Input'
        input_analog_typ_.Visible = 'on';
    case 'SCADA Input'
        min_typ_.Visible = 'on';
        max_typ_.Visible = 'on';
        def_value_typ_.Visible = 'on';
       
end


clear mask_typ_ input_analog_typ_ input_digital_typ_ invert_typ_  min_typ_  max_typ_ def_value_typ_
