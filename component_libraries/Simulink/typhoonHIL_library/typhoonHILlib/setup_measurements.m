% Update the Bus Selector block with chosen currents. Replaces the Outport
% with a Terminator if no current was selected.

function setup_measurements(blk, prompts, v_meas_params, i_meas_params)

range = 1:size(prompts, 2);

selected_str_v = '';
selected_str_i = '';
selected_meas_v = {};
selected_meas_i = {};

for i=range
    if strcmp(get_param(blk, v_meas_params{i}), 'on')
        selected_str_v = [selected_str_v 'v(' prompts{i} '),'];
    end
    if strcmp(get_param(blk, i_meas_params{i}), 'on')
        selected_str_i = [selected_str_i 'i(' prompts{i} '),'];
    end
end

if strcmp(selected_str_v, "") % Check if empty
    replace_blk([getfullname(blk) '/v_meas'], 'built-in/Terminator');
else
    selected_str_v = selected_str_v(1:end-1); %Remove last comma
    replace_blk([getfullname(blk) '/v_meas'], 'built-in/Outport');
    set_param([getfullname(blk) '/Selector_v'], 'OutputSignals', selected_str_v);
end

if strcmp(selected_str_i, "") % Check if empty
    replace_blk([getfullname(blk) '/i_meas'], 'built-in/Terminator');
else
    selected_str_i = selected_str_i(1:end-1); %Remove last comma
    replace_blk([getfullname(blk) '/i_meas'], 'built-in/Outport');
    set_param([getfullname(blk) '/Selector_i'], 'OutputSignals', selected_str_i);
end