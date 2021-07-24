% Finding the percentage of initial size:
[sizex, sizey, size_str] = get_blocksize(gcb);
xpcent = sizex/160; ypcent = sizey/200;
old_size = get_param(gcb, 'old_size');

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

set_param(gcb,'backgroundcolor','[1 0 0]')

% Won't redraw while resizing (waits for MoveFcn)
% Otherwise resizing can be very slow
if strcmp([num2str(sizex) ',' num2str(sizey)], old_size)

    conttype = get_param(gcb,'ContType');

    switch conttype
        case 'Single Pole Single Throw'
            conttype_txt = 'SPST';
            isST = true;
        case 'Single Pole Double Throw'
            conttype_txt = 'SPDT';
            isST = false;
        case 'Double Pole Single Throw'
            conttype_txt = 'DPST';
            isST = true;
        case 'Double Pole Double Throw'
            conttype_txt = 'DPDT';
            isST = false;
        case 'Triple Pole Single Throw'
            conttype_txt = 'TPST';
            isST = true;
        case 'Triple Pole Double Throw'
            conttype_txt = 'TPDT';
            isST = false;
        case 'Select the'
            conttype_txt = 'Select the';
            isST = true;
    end

    init_state = get_param(gcb, 'init_state');
    if ~isST
        if strcmp(init_state, 'On / S1')
            imgfile = 'DTS1.png';
        else
            imgfile = 'DTS2.png';
        end
    else
        if strcmp(init_state, 'On / S1')
            imgfile = 'STON.png';
        else
            imgfile = 'STOFF.png';
        end
    end

    comp_string = [conttype_txt ' Contactor'];


    if sizex>100&sizey>150
        im_x = 0.5/xpcent; im_y = 0.5*160/200/ypcent;
        image(['images/Contactor/' imgfile],[(1-im_x)/2 (1.3-im_y)/2 im_x im_y]);

        if newver == false
            logo_x = 0.25/xpcent; logo_y = 0.12/ypcent;
            image('images/elephant.png',[(1-logo_x)/2 (0.04) logo_x logo_y]);
        end

        patch([0.0 0.0 1 1], [0.21 0.35 0.35 0.21], [1 1 1]);
        text(0.5, 0.285, comp_string, 'horizontalAlignment', 'center');
    else
        image('images/elephant.png',[0.30 0.35 0.4 0.3]);
    end
end
