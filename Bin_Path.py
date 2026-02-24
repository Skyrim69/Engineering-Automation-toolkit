#Bin_Path.py script

import shutil
import os

ELF_PATH ="Bin file path"
S19_PATH ="Bin file path"

Destination = "Destination path to store these files"

class Binarypath(object):

    def Copybinaries(self):
        try :
            for path in [ELF_PATH, S19_PATH]:
                if os.path.exists(path):
                    destination_path = os.path.join(Destination, os.path.basename(path))
                    
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                        print(f"Existing file {os.path.basename(destination_path)} removed from {Destination}")

                    shutil.copyfile(path, destination_path)
                    print(f"File {os.path.basename(path)} copied to {destination_path}")
                    
        except Exception as e:
            print(f"Error copying file: {e}")