thisBlock = gcb;
mask = Simulink.Mask.get(thisBlock);
status = get_param(bdroot, 'SimulationStatus');

if strcmp(status, 'stopped')&~strcmp(bdroot,'typhoonHILlib')

    % Look for TSE versions in the TYPHOONPATH environment variable in order to
    % choose the correct Python executable
    lib_path_split = strsplit(which('typhoonHILlib'),'\');
    lib_path = strjoin(lib_path_split(1:end-1),'\');
    [ignore out] = system(['"' lib_path '\find_installed_tse_versions.bat"']);
    detected_versions = strsplit(out,',');
    if size(detected_versions, 2) > 0
        start_button = mask.getDialogControl('start_button');
        start_button.Enabled = 'on';
               
        % Remove newline character output from the batch script
        temp_str = detected_versions{end};
        temp_str = temp_str(1:end-1);
        detected_versions = strrep(detected_versions, detected_versions{end}, temp_str);
        
        % Add only compatible versions to the versions ComboBox
        combo_versions = {};
        for idx=1:size(detected_versions, 2)
            [ignore out] = system(['type "' detected_versions{idx} '\.version"']);
            if size(out) < 20 % Will be >20 if the .version file was not found (incompatible CC version)
                combo_versions{end+1} = detected_versions{idx};
            end
        end
        
        % Update the ComboBox with the detected versions
        versions_param = mask.getParameter('versions');
        if size(combo_versions, 2) > 0
            convert_text = mask.getDialogControl('convert_text');
            convert_text.Prompt = 'Waiting for the user command.';
            versions_param.TypeOptions = combo_versions(1:end);
        else
            start_button = mask.getDialogControl('start_button');
            start_button.Enabled = "off";
        end
        
    end

end