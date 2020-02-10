# Folder Structure Creator

## About
The folder structure creator is a small tool to make predefined folder hierachies.
The tool also supports the creation or copying of files.

## Features
- Standalone tool
- Python module
- Dynamic folder creation
- Create empty file object
- Copy file objects with absolute or relative paths

## Usage
### Standalone Tool

The standalone tool needs as inputs a path to the creation root and json file object
containing the folder structure. Through the use of python string Template pattern
dynamic values can by predefined. The optional template json file object can be
supplied to provide the key, value pairs for the string.Template substition.
The file values in the folder json can be a string, absolute or relative (to folder
json) paths.

Commadline options:

    -r, --root -> Path to creation root
    -f, --folders -> Path to json file containing the folder structure
    -t, --template -> Path to template json containing dynamic value
                      pairs for python string.template substition
    -v -> Set verbosity level for logging e.g. -vv = info

### Python module
The module is split in separate functions. Here is the execution flow:

```python
# Module import
from folder_structure_creator import folder_structure_creator as fsc

# Read the folder json file
folder_dict = fsc.read_json(folder_json)

# Create for all nested dict values a full path string as key and files as values
folder_dict = fsc.get_directories(folder_dict)

# Read the template josn file
string_replacement = fsc.read_json(args.template)

# Replace all occurences of string.templates in the folder and files
folder_dict = fsc.prep_directories(folder_dict, string_replacement)

# Create the directories
fsc.create_directories(folder_dict, creation_root)

# Create or copy the files to destination
fsc.create_files(folder_dict, creation_root, os.path.dirname(folder_json))
```
The module can be used to automatically create predefined folder structures. It is
possible to create a nested execution order.
The json objects can be replaced by standard python dictionaries.

## Licensing
Apache License, Version 2.0

## Authors
Wilfried Pollan - Maintainer

## Versioning
See https://semver.org

0.1.0 - First release - basic module and cmd version
