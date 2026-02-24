#Source_Path_Modify.py script

import shutil
import os

Destination = "Original source files to be placed in this path"

class FileCopy(object):

    def copy_files(self, file_paths):
        try:
            # Ensure destination directory exists
            if not os.path.exists(Destination):
                os.makedirs(Destination)

            for path in file_paths:
                if os.path.exists(path):
                    destination_path = os.path.join(Destination, os.path.basename(path))

                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                        print("\n"f"Existing file {os.path.basename(destination_path)} removed from {Destination}")

                    shutil.copyfile(path, destination_path)
                    print("\n"f"File {os.path.basename(path)} copied to {destination_path}")

        except Exception as e:
            print(f"Error copying file: {e}")

