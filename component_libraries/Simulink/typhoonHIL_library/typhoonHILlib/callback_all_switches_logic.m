% logic = 'high' or 'low'
% switches = {'sa1_logic' 'sa2_logic' 'sa3_logic' 'sa4_logic' ... }
function callback_all_switches_logic(logic, switches)
    
    status_typ_ = get_param(bdroot, 'SimulationStatus');

    if strcmp(status_typ_, 'stopped')
        
        mask_typ_ = Simulink.Mask.get(gcb);
           
        toggle_init_param_typ_ = mask_typ_.getParameter('toggle_init');
        toggle_draw_param_typ_ = mask_typ_.getParameter('toggle_draw');
        
        % Needed for fast toggling
        toggle_init_param_typ_.Value = 'off'; toggle_draw_param_typ_.Value = 'off';
        
        if strcmp(logic, 'high')
            cellfun(@(x) set_param(gcb, x, 'Active-high'), switches)
        elseif strcmp(logic, 'low')
            cellfun(@(x) set_param(gcb, x, 'Active-low'), switches)
        end

        toggle_init_param_typ_.Value = 'on'; toggle_draw_param_typ_.Value = 'on';

        clear mask_typ_ toggle_init_param_typ_ toggle_draw_param_typ_

    end
    
    clear status_typ_

end