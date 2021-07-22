mask_typ_ = Simulink.Mask.get(gcb);

convert_text_typ_ = mask_typ_.getDialogControl('convert_text');
version_typ_ = get_param(gcb, 'versions');
device_typ_ = get_param(gcb, 'device');
compile_typ_ = get_param(gcb, 'compile');
if strcmp(compile_typ_, 'on')
    compile_str_typ_ = 'True';
else
    compile_str_typ_ = 'False';
end

[ignore_typ_ out_typ_] = system(['type "' version_typ_ '\.version"']);

if bdIsDirty(gcs)
    convert_text_typ_.Prompt = "<font color='orange'>In progress... (ignoring unsaved changes)</font>";
else
    convert_text_typ_.Prompt = "<font color='orange'>In progress...</font>";
end

% Get the path to the current open .slx file
slx_filepath_typ_ = which(bdroot);
% Get the path to the Typhoon library
lib_path_split_typ_ = strsplit(which('typhoonHILlib'),'\');
lib_path_typ_ = strjoin(lib_path_split_typ_(1:end-1),'\');
disp('Initializing the conversion...')
[ignore_typ_ out_typ_] = system(['"' lib_path_typ_ '\tse_convert.bat" ' '"' out_typ_ '" "' slx_filepath_typ_ '" "' device_typ_ '" "' compile_str_typ_ '"']);

% Check the output from tse_convert.bat to determine success or failure.

if contains(out_typ_, 'Done. Check the report.txt file located')
    convert_text_typ_.Prompt = "<font color='green'>Finished.</font>";
    disp("Done. Check the report.txt file located in the source file's folder for more info.");
else
    convert_text_typ_.Prompt = ["<font color='red'>Failed. Please check the Command Window.</font>"];
    disp(['Could not complete the conversion:' newline out_typ_]);
end

clear compile_str_typ_     convert_text_typ_    ignore_typ_          lib_path_typ_        slx_filepath_typ_    
clear compile_typ_         device_typ_          lib_path_split_typ_  out_typ_             version_typ_         
