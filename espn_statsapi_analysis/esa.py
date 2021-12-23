#!/usr/bin/env python
""" ESPN-statsapi analysis runner script. """
import argparse
import esa_logger
import importlib
import inspect
import multiprocessing
import os
import sys
import timeit
import toml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
logger = esa_logger.logger()

sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
from espn_loader import EspnLoader
from statsapi_loader import StatsapiLoader

def _get_import_modules_from_toml_list(modules_list, root_modules_path=None):
    """ Helper function to return a list of modules to import based on
        the list found in the TOML that specifies which stats are ran.
        Each element in the list is relative to the "modules" folder in
        the same location as the ESA script. Returns a list intended to
        be directly used with dynamically importing other files using
        importlib functions.

        Examples:
          - "file1" -> "modules.file1"
          - "folder.file2 -> "modules.folder.file2"
          - "folder.folder2.file3 -> "modules.folder.folder2.file3"

        Also, handles case where ".*" operator looks for all files in
        the folder to import.

        Example:
          - ".*" will look for all .py files in the "modules" folder
            and will add all of them to the return list.
          - "folder.*" will look for all .py files in "folder", etc.
          - Note: ".*" operator only applies for files in that folder
            specified. Does not recursively add sub-folders and files.

        Example:
          - "folder.*" will add to the return list:
            ["folder.<file1>", "folder.<file2>", ...]
    """
    # Error check
    if not isinstance(modules_list, list):
        return []

    # First, check for root module path override
    # If supplied, use the folder name as the root modules path
    # Otherwise, use default name
    modules_name = "modules"
    modules_root_path = os.path.join(SCRIPT_DIR, modules_name)
    if root_modules_path is not None:
        modules_name = os.path.basename(root_modules_path)
        modules_root_path = root_modules_path

    # Iterate through each element and add modules to import to list
    temp_list = []
    for m in modules_list:
        # First handle ".*" (all in folder) case
        if m.endswith(".*"):
            # Look for files within the folder
            folder_structure = m.strip(".*")
            folder_structure_list = folder_structure.split(".")
            folder_search_path = os.path.join(modules_root_path, *folder_structure_list)

            # Search for all python files and add to the return lists
            for f in os.listdir(folder_search_path):
                path = os.path.join(folder_search_path, f)
                if os.path.isfile(path) and f.lower().endswith(".py"):
                    f_name = f.strip(".py")
                    if folder_structure == "":
                        temp_list.append(f"{modules_name}.{f_name}")
                    else:
                        temp_list.append(f"{modules_name}.{folder_structure}.{f_name}")

        # Otherwise, assume single file case
        else:
            temp_list.append(f"{modules_name}.{m}")

    # Remove any duplicates from the list.
    # This could be from user error, or from the possibility where
    # elements in the list specified the ".*" operator for a folder,
    # as well as individual files for the same folder.
    # Example: ["folder.*", "folder.file1", "folder.file2"]
    ret_list = []
    for m in temp_list:
        if m not in ret_list:
          ret_list.append(m)

    return ret_list

def _get_module_name_class(inspect_list, module_name):
    """ Given a list of tuples that is returned from inspect.getmembers() and
        the module name, find the correct class to dynamically import. This
        can occur when trying to dynamically look for classes in a file but
        contains/uses/inherits multiple other classes.

        Example:
        module_name = "child_class"
        inspect_list = [('BaseClass', <class>),
                        ('ChildClass', <class>),
                        ('AnotherClass', <class>)]

        Example returns "ChildClass" and its corresponding <class> object. """
    for name, cl in inspect_list:
        module_name_stripped = module_name.replace("_", "")
        if module_name_stripped == name.lower():
            return name, cl

def _import_and_process_module(m, espn_loader, statsapi_loader, out_path):
    """ Wrapper function to dynamically import and run the process()
        method of the given module. """
    # Dynamically import the module
    module = importlib.import_module(m)
    module_base_name = m.split(".")[-1]

    # Find the correct class to import within the module and run
    inspect_list = inspect.getmembers(module, inspect.isclass)
    name, cl = _get_module_name_class(inspect_list, module_base_name)
    module_class = getattr(module, name)
    m_obj = module_class(espn_loader, statsapi_loader,
                         os.path.join(out_path, module_base_name))

    logger.info(f"Processing: {m}.{name}")
    m_obj.process()

if __name__ == "__main__":
    """ Entry point for ESA. """
    # Timing
    start_time = timeit.default_timer()

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--espn", required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    arg_parser.add_argument("--statsapi", required=True, help="Root path of statsapi data cache from statsapi downloader.")
    arg_parser.add_argument("--outdir", required=True, help="Path to folder where output data will go.")
    args = arg_parser.parse_args()

    # Data paths
    espn_data_path = args.espn
    statsapi_data_path = args.statsapi
    out_path = args.outdir
    cfg_path = os.path.join(SCRIPT_DIR, "cfg.toml")

    # Read config file
    cfg_dict = toml.load(open(cfg_path, 'r'))
    modules_to_run = _get_import_modules_from_toml_list(cfg_dict['modules']['run_list'])

    # Instantiate data loaders to pass into modules below
    espn_loader = EspnLoader(espn_data_path)
    statsapi_loader = StatsapiLoader(statsapi_data_path)

    # Import all modules in list and run its functions using multi-processing
    # Each module will run on its own process
    p = multiprocessing.Pool(os.cpu_count())
    for m in modules_to_run:
        async_result = p.apply_async(func=_import_and_process_module,
                                     args=[m, espn_loader, statsapi_loader, out_path])
    p.close()
    p.join()

    # Print any results from processes, such as exceptions
    result = async_result.get()
    if result is not None:
        print(result)

    # Done
    logger.info(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")