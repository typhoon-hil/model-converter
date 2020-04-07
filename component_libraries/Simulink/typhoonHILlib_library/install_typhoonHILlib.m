bdclose all;
typhoon_lib_name = 'typhoonHILlib';

if ~isempty(which(typhoon_lib_name,'-all'))
    disp('The Typhoon HIL library was already detected on your system.');
    lib_found = what(typhoon_lib_name);
    detected_installation = lib_found.path;
    disp(['Installation folder: ' detected_installation]);
    disp(['If you wish to update the library, please close MATLAB, delete the '...
        typhoon_lib_name ' folder and run the installation script again.']);
else
    
    disp(['Please choose where you wish to copy the ' typhoon_lib_name ' folder to.']);
    install_path = uigetdir([getenv('userprofile') '\Documents'], 'Select a folder for the installation of the library');
    
    if ~exist(typhoon_lib_name,'dir') 
        error(['Cannot find the folder named ' typhoon_lib_name ', which is needed for the installation process.']);
    end
    
    destination_folder = [install_path '\' typhoon_lib_name];
    try  
        copyfile(typhoon_lib_name, destination_folder);
    catch
        error(['Problem while copying the ' typhoon_lib_name ' folder to ' install_path '. Please try copying manually.']);
    end
    
    installed_lib_path = [install_path '\' typhoon_lib_name];
    if exist(installed_lib_path, 'dir')
        disp([typhoon_lib_name ' folder copied successfully. Updating PATH...']);

        addpath(installed_lib_path);
        addpath([installed_lib_path '\Images']);
        addpath([installed_lib_path '\Images\Contactor']);
        addpath([installed_lib_path '\Images\Core Coupling']);
        addpath([installed_lib_path '\Images\Machine']);
        addpath([installed_lib_path '\Images\Switching Leg']);
        addpath([installed_lib_path '\Images\Transformer']);
        addpath([installed_lib_path '\Images\Transmission Line']);
        savepath;
        
        disp('Installation complete.');
    end
    
end

