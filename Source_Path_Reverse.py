#Source_Path_Reverse.py script

import shutil
import os
import Source_code_Modification

SOURCEPATH = "Original source files to be stoutilised from this pa."

class RevertPath(object):
    
    def Revertsourcefiles(self):
        try :
            scm = Source_code_Modification.SourceCodeModification()
            scm.detect_modules()
            Modules = scm.Active_Modules

            if not Modules:
                print("[INFO] No active modules for this stage.")
                return
            
            FILES = scm.ALL_MODULES

            for module in Modules:
                file = FILES[module]["file"]
                Source_path = os.path.join(SOURCEPATH, file.name)

                if not os.path.exists(Source_path):
                    print(f"Source file {Source_path} does not exist.")
                    continue

                Destination_Path = str(file) 

                shutil.copyfile(Source_path, Destination_Path)
                print(f"Copied {Source_path} to {Destination_Path}")

        except Exception as e:
            print(f"Error copying file: {e}")
