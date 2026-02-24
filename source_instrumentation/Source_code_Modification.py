import os
from pathlib import Path
import argparse
import sys
import Source_Path_Modify
import Source_Path_Reverse
import Bin_Path

# Stage to module mapping (generalized)
STAGE_MODULE_MAP = {
    "stage_alpha": ["MODULE_A", "MODULE_B"],
    "stage_beta": ["MODULE_C"],
    "stage_gamma": ["MODULE_D", "MODULE_E"]
}

class SourceCodeModification():
    
    WORKSPACE = Path(os.environ.get("WORKSPACE", Path.cwd()))
    SOURCE_ROOT = WORKSPACE / "sample_project" / "modules"

    ALL_MODULES = {
        "MODULE_A": {
            "file": SOURCE_ROOT / "module_a.c",
            "function": "PeriodicFunction_10ms",
            "test_variable": "Uint16 test_counter_start = 0, test_counter_end;",
            "increment": "++test_counter_start;",
            "assignment": "test_counter_end = test_counter_start;"
        },
        "MODULE_B": {
            "file": SOURCE_ROOT / "module_b.c",
            "replace": {"(void) Rte_Call(&Module.Structure);": "(void) Rte_Call(&Test_Module.Structure);"},
            "insert_below": {"B_APP_SWC_Component_T Module;": ["B_APP_SWC_Component_T Test_Module;"]},
            "function": "PeriodicFunction_20ms",
            "test_variable": "Uint16 test_counter_start = 0, test_counter_end;",
            "increment": "++test_counter_start;",
            "assignment": "test_counter_end = test_counter_start;"
        }
    }


    def replace_multiple_strings(self, file_path, replacements):
        """Replace multiple strings in a single file."""
        if not os.path.isfile(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return

        with open(file_path, "r") as f:
            content = f.read()

        original_content = content

        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                print(f"[OK] Replaced '{old}' -> '{new}' in {file_path}")
            else:
                print(f"[INFO] '{old}' not found in {file_path}")

        if content != original_content:
            with open(file_path, "w") as f:
                f.write(content)

    def insert_strings_below_targets(self, file_path, insert_map):
        """
        insert_map = {
            "target_string1": ["line_to_insert_1", "line_to_insert_2"],
            "target_string2": ["line_to_insert_x"]
        }
        """
        if not os.path.isfile(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return

        with open(file_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        existing_lines = set(line.strip() for line in lines)
        
        for line in lines:
            new_lines.append(line)
            for target, insert_list in insert_map.items():
                if target in line:
                    for ins in insert_list:
                        if ins not in existing_lines:
                            new_lines.append(ins + "\n")
                        existing_lines.add(ins)
                    print(f"[OK] Inserted text below '{target}' in {file_path}")

        with open(file_path, "w") as f:
            f.writelines(new_lines)

    def insert_Test_variables(self, file_path, variables, functions, incrementals, assignments):

        if not os.path.isfile(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return
        
        with open(file_path, "r") as f:
            content = f.readlines()

        Lines = "".join(content)
        new_lines = []
        function_found = False
        increment_inserted = False
        inside_rte_write = False
        last_rte_index = None

        if isinstance(functions, list):
            function_list = functions
        else:
            function_list = [functions]

        for line in content:

            # insert initialisation variables
            if not function_found and any(func in line for func in function_list)and "(" in line and ")" in line:

                for var in variables:
                    if var not in Lines:
                        new_lines.append( var + "\n\n")
                function_found = True
            new_lines.append(line)

            # detect function by entry brace and add incremental start variable
            if (function_found and not increment_inserted and "{" in line):
                for inc in incrementals:
                    if inc not in Lines:
                        new_lines.append("\n"+" "+" "+inc +"\n\n")
                increment_inserted = True

            # detect RTe write string
            if function_found and "Rte_Write" in line :
                inside_rte_write = True

            #check if " ; " found in same line or one line below 
            if inside_rte_write and ";" in line:
                last_rte_index =  len(new_lines) - 1
                inside_rte_write = False

        #insert Data transfer after last rte write string. 
        if last_rte_index is not None:
            insert_index = last_rte_index + 1
        else:
            # Find function closing brace
            brace_count = 0
            insert_index = None
            inside_tarted_function = False

            for i, line in enumerate(new_lines):
                if any(func in line for func in function_list) and "(" in line:
                    inside_tarted_function = True
                
                if inside_tarted_function:
                    brace_count += line.count("{")
                    brace_count -= line.count("}")

                    if brace_count == 0 and "}" in line:
                        insert_index = i
                        break

            if insert_index is None:
                insert_index = len(new_lines) - 1
        
        for asgn in assignments:
            if asgn not in Lines:
                new_lines.insert(insert_index,"\n"" "+" "+asgn +"\n\n")
                insert_index += 1

        with open(file_path, "w") as f:
            f.writelines(new_lines)
            print(f"Inserted {variables} in file {file_path}")
            print(f"Inserted {incrementals} in function {functions}")
            print(f"Inserted {assignments} in file {file_path}")


    def process_specific_c_files(self, file_actions): 
        
        for file_path, actions in file_actions.items():
            file_path = Path(file_path)
            print(f"\n===== Processing {file_path} =====")
            if "replace" in actions:
                self.replace_multiple_strings(file_path, actions["replace"])
            if "insert_below" in actions:
                self.insert_strings_below_targets(file_path, actions["insert_below"])
            if "TestVariable" in actions and "FunctionName" in actions and "Increment" in actions and "Assignment" in actions:
                self.insert_Test_variables(file_path , actions["TestVariable"],actions["FunctionName"],actions["Increment"],actions["Assignment"])


    def process_modules(self):
        self.detect_modules()
        print(f"Active Modules for stage '{self.stage_name}': {self.Active_Modules}")

        if not self.Active_Modules:
            print(f"[INFO] No Active modules for stage: {self.stage_name}")
            return

        for module in self.Active_Modules:
            if module not in self.ALL_MODULES:
                raise RuntimeError(f"Module '{module}' not found in ALL_MODULES configuration.")
            File = self.ALL_MODULES[module]
            actions = {
                "test_variable": File.get("test_variable",[]),
                "function": File.get("function",[]),
                "increment": File.get("increment",[]),
                "assignment": File.get("assignment",[]),
                "insert_below": File.get("insert_below", {}),
                "replace": File.get("replace", {})
            }
            self.process_specific_c_files({File["file"]: actions})


    def __init__(self):
        self.stage_name = os.environ.get("STAGE_NAME", "").lower()
        self.active_modules = []

    def detect_modules(self):
        for stage, modules in STAGE_MODULE_MAP.items():
            if stage in self.stage_name:
                self.active_modules = modules
                break
        
def main ():
        parser = argparse.ArgumentParser()

        parser.add_argument("--binarypath", action="store_true", help="Store original Binaries to a location.")
        parser.add_argument("--copysourcefiles", action="store_true", help="Store original source files to a location.")
        parser.add_argument("--modifysourcefiles", action="store_true", help="Modify source code for code change in .c files.")
        parser.add_argument("--reversesourcefiles", action="store_true", help="revert the changes made in modified files.")

        args = parser.parse_args()
        bin_obj = Bin_Path.Binarypath()

        try:
            if args.binarypath:
                bin_obj.Copybinaries()
                sys.exit(0)

            if args.copysourcefiles:
                scm = SourceCodeModification()
                scm.detect_modules()
                files_to_copy =[
                    scm.ALL_MODULES[module]["file"]
                    for module in scm.Active_Modules
                ]
                Source_Path_Modify.FileCopy().copy_files(files_to_copy)
                sys.exit(0)

            if args.modifysourcefiles:
                scm = SourceCodeModification()
                scm.process_modules()
                sys.exit(0)

            if args.reversesourcefiles:
                Source_Path_Reverse.RevertPath().Revertsourcefiles()
                sys.exit(0)
                
        except RuntimeError as my_exception:
            print(f"Exception :{my_exception}")
            sys.exit(-1)


if __name__ == "__main__":
    main()



