% Get the block size and the corresponding string for the
% old_size parameter

function [sizex, sizey, size_str] = get_blocksize(blk)

    pos = get_param(blk,'Position');
    sizex = pos(3)-pos(1);
    sizey = pos(4)-pos(2);
    size_str = [num2str(sizex) ',' num2str(sizey)];
    
end