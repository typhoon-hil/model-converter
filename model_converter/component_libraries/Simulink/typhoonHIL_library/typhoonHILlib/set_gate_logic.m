% Uncomment gate signal inverter if 'Active-low' is selected for a switch

function set_gate_logic(blk, logic_params)

for i=1:size(logic_params,2)
    selected_logic = get_param(blk,logic_params{i});
    inv_blk = [getfullname(blk) '/inv' num2str(i)];
    if strcmp(selected_logic,'Active-low')
        set_param(inv_blk,'Commented','off');
    else
        set_param(inv_blk,'Commented','through');
    end
end

end
