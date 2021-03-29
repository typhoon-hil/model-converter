% Finding the percentage of initial size:
[sizex, sizey, size_str] = get_blocksize(gcb);
xpcent = sizex/160; ypcent = sizey/200;
old_size = get_param(gcb, 'old_size');
tog_draw = strcmp(get_param(gcb,'toggle_draw'),'on');
y_delta = 0;

% 2019b+ changed image() function
versionstr = version();
versionstr_split = split(versionstr, ".");
v1 = str2num(versionstr_split{1});
v2 = str2num(versionstr_split{2});
if v1 > 8 && v2 > 6
    newver = true;
else
    newver = false;
end

set_param(gcb,'backgroundcolor','[1 0 0]');

% Won't redraw while resizing (waits for MoveFcn)
% Otherwise resizing can be very slow
if strcmp([num2str(sizex) ',' num2str(sizey)], old_size)&tog_draw
    three_phase = get_param(gcb,'ThreePhase');
    invtype_txt = get_param(gcb,'InvType');
    if strcmp('on', three_phase)
        comp_string1 = ['Three-Phase'];
        comp_string2 = [invtype_txt ' Inverter'];
    else
        comp_string1 = ['Single-Phase'];
        comp_string2 = [invtype_txt ' Inverter'];
    end

    if strcmp(invtype_txt,'Select the')
        comp_string1 = '';
        y_delta = 0.03;
    end

    if sizex>100&sizey>150
        im_x = 0.5/xpcent; im_y = 0.5*160/200/ypcent;
        image('images/DC-AC.png',[(1-im_x)/2 (1.3-im_y)/2 im_x im_y]);

        if newver == false
            logo_x = 0.25/xpcent; logo_y = 0.12/ypcent;
            image('images/elephant.png',[(1-logo_x)/2 (0.04) logo_x logo_y]);
        end

        patch([0.0 0.0 1 1], [0.21 0.35 0.35 0.21], [1 1 1]);
        text(0.5, 0.315, comp_string1, 'horizontalAlignment', 'center');
        text(0.5, 0.255 + y_delta, comp_string2, 'horizontalAlignment', 'center');
    else
        image('images/elephant.png',[0.30 0.35 0.4 0.3]);
    end
end
