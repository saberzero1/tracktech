"""This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

"""


import os
import sys
from pathlib import Path
import pkgutil
import pkg_resources
import pdoc
import mock
import dis
import importlib
import importlib.util


def generate_documentation(root_folder):
    """Generates pdoc documentation for all Python modules in CameraProcessor project.

    Args:
        root_folder (Path): path to root folder of Python code.
    """
    doc_folder = os.path.dirname(__file__)
    absolute_root_folder = os.path.join(os.path.dirname(doc_folder), root_folder)

    component_root = os.path.dirname(absolute_root_folder)

    # Points pdoc to used jinja2 template and sets Google docstrings as the used docstring format.
    pdoc.render.configure(template_directory=Path(os.path.join(doc_folder, 'template')),
                          docformat='google')

    # Add to_tree to Jinja2 environment filters to generate tree from modules list.
    pdoc.render.env.filters['to_tree'] = to_tree

    # Output directory
    output_dir = Path(os.path.join(doc_folder, 'html', root_folder))

    # Create docs html dir if it doesn't exist.
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all modules included by pdoc, respecting the __all__ attribute in __init__.py.
    included_paths = get_modules(absolute_root_folder)

    # Create module imports from included paths.
    included_modules = [path_to_module(component_root, included_path) for included_path in included_paths]

    mock_modules = set()

    # Create mock for all import statements not included in included_modules.
    for included_module in included_paths:
        # Get imports of module from included module.
        module_imports = get_imports(included_module)

        # Loop over all found imports.
        for module_import in module_imports:
            # Get all possible module parts.
            for module_import_part in get_module_import_parts(module_import):
                # Create mock if module part hasn't been included yet.
                if module_import_part not in included_modules:
                    mock_modules.add(module_import_part)

    installed_packages = [p.project_name for p in pkg_resources.working_set]

    # Add mock if sys.modules doesn't include an import statement or if the package is already installed.
    for mod_name in mock_modules:
        # Don't mock object if it has already been installed.
        skip = False
        for package in installed_packages:
            if mod_name == package or mod_name.startswith(f'{package}.'):
                skip = True

        if skip:
            continue

        if mod_name not in sys.modules:
            mod_mock = mock.Mock(name=mod_name)
            sys.modules[mod_name] = mod_mock

    # Generate documentation for all found modules in the /docs.
    pdoc.pdoc(absolute_root_folder, output_directory=output_dir)


def get_imports(file_path):
    """Get all import names from import statements used in the Python file located at file_path.

    Args:
        file_path (str): path to the module, can be the python file, or dir name containing an __init__.py.

    Returns:
        List[str]: list of import names.
    """
    # Check if Python module exists and form path to open module.
    if file_path.endswith('.py') and Path.exists(Path(file_path)):
        py_file_path = file_path
    elif Path.exists(Path(f'{file_path}.py')):
        py_file_path = f'{file_path}.py'
    elif Path.exists(Path(f'{file_path}/__init__.py')):
        py_file_path = f'{file_path}/__init__.py'
    else:
        raise FileNotFoundError('Python module not found')

    # Open Python file as if it is a normal file.
    file = open(Path(py_file_path), encoding='UTF-8')

    # Get all instructions in Python file.
    instructions = dis.get_instructions(file.read())

    # Filter on IMPORT_NAME and IMPORT_FROM.
    instruction_names = ['IMPORT_NAME', 'IMPORT_FROM']

    # argval of allowed instruction arguments
    imports = [instruction.argval for instruction in instructions if instruction.opname in instruction_names]

    return imports


def get_modules(root_folder):
    """Gets all modules starting from the top folder,
    excludes Python modules that are deemed as hidden.

    Gets all modules starting from the top folder given as root_folder.
    Starts by searching for all sub folders of the root folder,
    excluding folders starting with '.' or '_'.
    Looks for modules in all found folders (root_folder + both direct and indirect sub folders).

    Args:
        root_folder (str): root folder to look through modules at current level and in the sub folders

    Returns:
        list[str]: list of all Python modules located in root_folder and its sub folders
    """
    # Append root_folder dirname to sys.path to import modules.
    component_root = os.path.dirname(root_folder)
    sys.path.append(component_root)

    # Find all valid sub folders (dir name doesn't start with
    # '.' or '_', starting at the root_folder.
    folders = [root_folder]
    index = 0
    while index < len(folders):
        current_folder = folders[index]

        # Find all folders/directories in current folder, add full path if folder name doesn't start with '.' or '_'.
        for folder in os.scandir(current_folder):
            if not folder.is_dir() or folder.name.startswith('.') or folder.name.startswith('_'):
                continue

            folder_name = os.path.join(current_folder, folder.name)

            folders.append(folder_name)

        index += 1

    includes = dict()

    # Import all packages to retrieve the __all__ attribute (if there is one).
    for module in pkgutil.iter_modules(folders):
        if not module.ispkg:
            continue

        module_path = os.path.join(module.module_finder.path, module.name)

        import_path = path_to_module(component_root, module_path)

        # Package module shouldn't contain code with side effects.
        imported_module = importlib.import_module(import_path)

        # Get included modules from the __all__ attribute,
        # module excluded if it isn't inside the __all__ attribute if the __init__.py has an __all__ attribute.
        if hasattr(imported_module, '__all__'):
            all_included = getattr(imported_module, '__all__')
            includes[module_path] = all_included

    # Find all modules in found folders and append the full path.
    modules = [root_folder]
    for module in pkgutil.iter_modules(folders):
        if module.name.startswith('_'):
            continue

        module_path = os.path.join(module.module_finder.path, module.name)

        # Check if module is included.
        include = True
        for key in includes.keys():
            # Module isn't included if a valid key exists for any package it is in that doesn't include it via __all__.
            if key != module_path and key in module_path and module.name not in includes[key]:
                include = False
                break

        if include:
            modules.append(module_path)

    return modules


def path_to_module(component_root, path):
    """Turns a path into a module using the root as the starting place for module imports.

    Args:
        component_root (str): root to start import from.
        path (str): path to convert to module import.

    Returns:
        str: module import in Python notation.
    """
    # Remove path leading up to component root/path before import statement starts.
    module = path.replace(component_root, '')

    # Remove potential initial slash from path.
    if module.startswith('/') or module.startswith('\\'):
        module = module[1:]

    # Remove potential trailing slash from path.
    if module.endswith('/') or module.endswith('\\'):
        module = module[:-1]

    # Replace all slashes with dots.
    module = module.replace('/', '.').replace('\\', '.')

    # Path is now converted to module import.
    return module


def get_module_import_parts(module_import):
    """Get all module imports from an initial module import, this includes all higher level imports.

    module_import = 'example.module.import.part' generates the following list:
    [
        'example.module.import.part',
        'example.module.import',
        'example.module',
        'example'
    ]

    Args:
        module_import (str): initial module import to derive higher level imports from.

    Returns:
        List[str]: list of module import parts.
    """
    module_imports = [module_import]

    index = len(module_import) - 1
    while index > 0:
        if module_import[index] == '.':
            module_imports.append(module_import[:index])

        index -= 1

    return module_imports


def to_tree(modules):
    """Turn a list of modules into a dictionary representing a tree
    which gets turned into a JSON object by Jinja2.

    The tree dictionary contains a dictionary for each package/module.
    A module has an empty dictionary and packages leading up to
    a module are filled with all contained module dictionaries.

    Args:
        modules (list[str]): list of strings of all module paths (like used in an import statement).

    Returns:
        dict(str, dict): dictionary containing the tree structure as mentioned above.
    """
    tree = dict()

    for module in modules:
        module_path = module.split('.')
        subtree = tree
        for part in module_path:
            if part not in subtree:
                subtree[part] = dict()
            subtree = subtree[part]
    return tree


if __name__ == '__main__':
    import argparse

    # Set root_folder as required argument to call documentation.py.
    parser = argparse.ArgumentParser(description='Generate documentation for provided root folder')
    parser.add_argument('root_folder',
                        type=str,
                        help='Root folder containing all top-level modules. '
                             'Includes all modules included via __init__.py, '
                             'except for modules not included in __all__ inside __init__.py when provided.'
                        )

    # Parse arguments.
    args = parser.parse_args()

    # Prepend .. to args root_folder to start one level higher (starting at root of project).
    root = Path(args.root_folder)

    # Generate documentation for all packages included (via __init__ or if specified __all__ in __init__).
    generate_documentation(root)