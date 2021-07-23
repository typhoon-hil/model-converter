% Update the Bus Selector block with chosen currents. Replaces the Outport
% with a Terminator if no current was selected.

function setup_machine_terminals(blk)

meas = get_param(blk, 'enable_outputs');
if strcmp(meas,'on')
    if strcmp(get_param([getfullname(blk) '/w'], 'BlockType'),'Terminator')
        replace_blk([getfullname(blk) '/w'], 'built-in/Outport');
        replace_blk([getfullname(blk) '/T'], 'built-in/Outport');
        if ~(getSimulinkBlockHandle([getfullname(gcb) '/theta']) == -1)
            replace_blk([getfullname(blk) '/theta'], 'built-in/Outport');
        end
    end
else
    replace_blk([getfullname(blk) '/w'], 'built-in/Terminator');
    replace_blk([getfullname(blk) '/T'], 'built-in/Terminator');
    if ~(getSimulinkBlockHandle([getfullname(gcb) '/theta']) == -1)
        replace_blk([getfullname(blk) '/theta'], 'built-in/Terminator');
    end
end