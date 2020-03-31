function blkStruct = slblocks
		% This function specifies that the library should appear
		% in the Library Browser and be cached in the browser repository

		Browser.Library = 'typhoonHILlib';
                % The name of the library

		Browser.Name = 'Typhoon HIL';
                % The library name that appears 
                % in the Library Browser

		blkStruct.Browser = Browser;