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

set_param(gcb,'backgroundcolor','[1 0 0]');

% Won't redraw while resizing (waits for MoveFcn)
% Otherwise resizing can be very slow
if strcmp([num2str(sizex) ',' num2str(sizey)], old_size)&strcmp(get_param(gcb,'toggle_draw'), 'on');

    % .TypeOptions in callback_transmission_line triggers drawing
    % Using .Value instead of get_param() to avoid redrawing before applying
    mask = Simulink.Mask.get(gcb);
    linetype = mask.getParameter('LineType');
    linetype = linetype.Value;
    underground = mask.getParameter('underground');
    underground = underground.Value;
    comp_string1 = '';
    y_delta = 0.03;

    switch linetype
        case 'PI Section'
            if strcmp(underground, 'on')
                imgfile = 'Cable.png';
                comp_string1 = 'Underground Cable';
                comp_string2 = linetype;
                y_delta = 0;
            else
                imgfile = 'Section.png';
                comp_string2 = linetype;
            end
        case 'RL Section'
            imgfile = 'Section.png';
            comp_string2 = linetype;
        case 'Coupled RL'
            if strcmp(underground, 'on')
                imgfile = 'Cable.png';
                comp_string1 = 'Underground Cable';
                comp_string2 = linetype;
                y_delta = 0;
            else
                imgfile = 'Section.png';
                comp_string2 = linetype;
            end
        case 'Bergeron'
            imgfile = 'Bergeron.png';
            comp_string2 = linetype;
        case 'Select the'
            imgfile = 'Section.png';
            comp_string2 = [linetype ' Line Type'];
    end


    if sizex>100&sizey>150
        im_x = 0.5/xpcent; im_y = 0.5*160/200/ypcent;
        image(['images/Transmission Line/' imgfile],[(1-im_x)/2 (1.3-im_y)/2 im_x im_y]);

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
