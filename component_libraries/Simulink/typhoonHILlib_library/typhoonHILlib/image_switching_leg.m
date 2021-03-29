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

    legtype_txt = get_param(gcb,'LegType');
    ttype_txt = get_param(gcb,'Ttype');
    fclevels_txt = get_param(gcb,'FCLevels');
    y_delta = 0;

    if strcmp('Flying Capacitor', legtype_txt)
        comp_string1 = fclevels_txt;
    elseif strcmp('NPC', legtype_txt)
        if strcmp('on', ttype_txt)
            comp_string1 = ['T-Type'];
        else
            comp_string1 = [''];
            y_delta = 0.03;
        end
    else
        comp_string1 = [''];
        y_delta = 0.03;
    end
    comp_string2 = [legtype_txt ' Leg'];

    switch legtype_txt

        case 'Diode'
            img = 'Diode.png';
        case 'IGBT'
            img = 'IGBT.png';
        case 'Antiparallel Thyristor'
            img = 'AT.png';
        case 'NPC'
            if strcmp('on', ttype_txt)
                img = 'TNPC.png';
            else
                img = 'NPC.png';
            end
        case 'Flying Capacitor'
            img = 'FC.png';
    end

    if strcmp(legtype_txt,'Select the')
        comp_string1 = '';
        y_delta = 0.03;
        img = 'Diode.png';
    end

    if sizex>100&sizey>150
        im_x = 0.5/xpcent; im_y = 0.5*160/200/ypcent;
        image(['images/Switching Leg/' img],[(1-im_x)/2 (1.3-im_y)/2 im_x im_y]);

        if newver == false
            logo_x = 0.25/xpcent; logo_y = 0.12/ypcent;
            image('images/elephant.png',[(1-logo_x)/2 (0.04) logo_x logo_y]);
        end

        patch([0.0 0.0 1 1], [0.21 0.35 0.35 0.21], [1 1 1]);
        text(0.5, 0.315 - y_delta, comp_string1, 'horizontalAlignment', 'center');
        text(0.5, 0.255 + y_delta, comp_string2, 'horizontalAlignment', 'center');
    else
        image('images/elephant.png',[0.30 0.35 0.4 0.3]);
    end
end
