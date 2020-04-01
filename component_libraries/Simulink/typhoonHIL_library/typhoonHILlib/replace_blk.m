% Local replace function
% ex: replace_blk([blk,'/Out1'],'built-in/Terminator')
function replace_blk(oldblock,newblock)

pos = get_param(oldblock,'Position');
orient = get_param(oldblock,'Orientation');
delete_block(oldblock);
add_block(newblock,oldblock,'Position',pos,'Orientation',orient);
end