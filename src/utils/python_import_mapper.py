# %%
# Imports #

import argparse
import glob
import os
import re
import subprocess
import sys

# append grandparent
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_utils import great_grandparent_dir
from utils.display_tools import print_logger

# %%
# File Sources #


def get_imported_modules(file_content):
    """Extract imported modules from the file content."""
    imports = set()
    import_patterns = [
        re.compile(r"^import (\S+)", re.M),
        re.compile(r"^from (\S+) import", re.M),
    ]

    for pattern in import_patterns:
        for match in pattern.findall(file_content):
            imports.add(match)

    return imports


def check_if_module_in_list(ls_modules, module_name, include_utils=False):
    if "config" in module_name:
        return False

    if module_name != module_name:
        return False

    if include_utils:
        split_mod_name = module_name.split(".")
        if len(split_mod_name) > 1:
            module_name = split_mod_name[1]

    if module_name in ls_modules:
        return True


def generate_python_map(folder_path_to_map, output_file_path, include_utils=False):
    python_files = {}
    relationships = []

    # 1. Walk through folder and gather all python files
    for root, _, files in os.walk(folder_path_to_map):
        for file in files:
            if (
                file.endswith(".py")
                and ("checkpoint" not in file)
                and ("config" not in file)
            ):
                print(f"Found python file: {file}")
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, folder_path_to_map)
                module_name = file[:-3]  # Remove .py extension

                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                python_files[module_name] = {
                    "path": relative_path,
                    "imports": get_imported_modules(content),
                }

    # 2. Determine relationships
    for module_name, file_data in python_files.items():
        for imported_module in file_data["imports"]:
            if check_if_module_in_list(
                python_files.keys(), imported_module, include_utils=include_utils
            ):
                relationships.append((imported_module, module_name))

    # 3. Write markdown file with LR chart
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("# Mermaid\n")
        f.write("\n")
        f.write("```mermaid\n")
        f.write("graph LR;\n")
        f.write("\n")
        for relationship in relationships:
            f.write(f"{relationship[0]} --> {relationship[1]}\n")
        f.write("```\n")


def find_unused_functions(project_dir):
    def find_functions(project_dir):
        functions = []
        # Get all Python files in the src directory (no subdirectories)
        py_files = glob.glob(os.path.join(project_dir, "*.py"))

        for py_file in py_files:
            # Use grep to find all function definitions in each file
            result = subprocess.run(
                ["grep", "-P", "-nw", r"def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", py_file],
                capture_output=True,
                text=True,
            )
            lines = result.stdout.splitlines()
            for line in lines:
                # Extract function name from the grep output
                func_name = line.split("def ")[1].split("(")[0].strip()
                functions.append(
                    (func_name, py_file)
                )  # Save function name and file location
        return functions

    def check_function_usage(func_name, project_dir):
        py_files = glob.glob(os.path.join(project_dir, "*.py"))
        # Ensure we're passing the correct list of files to grep
        result = subprocess.run(
            ["grep", "-rnw"] + py_files + ["-e", func_name],
            capture_output=True,
            text=True,
        )
        return result.stdout

    unused_functions = []
    all_functions = find_functions(project_dir)

    for func in all_functions:
        usage = check_function_usage(
            func[0], project_dir
        )  # Use func[0] for function name
        # If only one occurrence, it means it's only in the definition
        if usage.count("\n") == 1:
            unused_functions.append(func)

    if unused_functions:
        print("Unused functions:")
        for func in unused_functions:
            print(f"- {func}")
    else:
        print_logger("No unused functions found.")

    return unused_functions


# %%
# File Sources #


if __name__ == "__main__":
    folder_path_to_map = os.path.join(great_grandparent_dir, "na-finops", "src")
    output_file_path = os.path.join(
        great_grandparent_dir, "na-finops", "docs", "Python_Relationship_Chart.md"
    )
    include_utils = False

    if "ipykernel" in sys.argv[0]:
        print("Running in IPython kernel")
    else:
        parser = argparse.ArgumentParser(description="Generate python path map.")
        parser.add_argument("-p", "--path", type=str, help="Folder path to map")
        parser.add_argument(
            "-o",
            "--output_file",
            type=str,
            help="File path of output file (.md)",
        )
        parser.add_argument(
            "-u",
            "--include_utils",
            action="store_true",
            help="Include utils in the mapping",
        )

        args = parser.parse_args()

        if args.path:
            folder_path_to_map = args.path
        if args.output_file:
            output_file_path = args.output_file
        if args.include_utils:
            include_utils = True

    print_logger(
        f"Folder path to map: {folder_path_to_map} being mapped to output file: {output_file_path}"
    )
    generate_python_map(folder_path_to_map, output_file_path, include_utils)
    print_logger(
        f"Folder path to map: {folder_path_to_map} was mapped to output file: {output_file_path}"
    )

    print_logger(f"Checking for unused functions in {folder_path_to_map}")
    ls_unused_functions = find_unused_functions(folder_path_to_map)


# %%
