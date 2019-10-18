#!/usr/bin/env python

# Copyright 2019 Wilfried Pollan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   # http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Create a folder structure based on a dict.

file=folder_structure_creator.py

This script can be used standalone or imported as a module to create a folder
structure. It's possible to define dynamic values in the folder dict and
replace them during the execution with second supplied substition dict.

Inputs for standalone:
1. <path>; path to creation root
2. <path>; json folder dict
3. <path>; json template dict, dynamic values for string.template substition
"""


__author__ = 'Wilfried Pollan'


# Imports
import sys
import os
import json
import logging
import shutil
from string import Template


# Read json folder template
def read_json(json_path):
    """
    Read the json file and return the dict.

    :params json_path: path to json file
    :type json_path: str
    :return: json data as python dict
    :rtype: dict
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # function routines
    with open(json_path) as fobjs:
        logger.debug('Loading json: {0}'.format(json_path))
        return json.load(fobjs)


# Create dict with directories to create
def get_directories(json_dict, parent_key=None):
    """
    Join the dict keys with os.sep to create path key and file element pairs.

    :params json_dict: A dict where each key represent a leaf folder
               and the values are files
    :type json_dict: dict
    :params parent_key: Internal used in the recursive function call.
    :type parent_key: str
    :return: A dict of folder path, file list pairs
    :rtype: dict
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # Init variables
    sep = os.sep
    items = []

    # function routines
    for k, v in json_dict.items():
        logger.debug('Processing: {0}, {1}'.format(k, v))
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(get_directories(v, parent_key=new_key).items())
        else:
            if isinstance(v, list):
                items.append((new_key, v))
            elif isinstance(v, basestring):
                items.append((new_key, [v]))
            else:
                raise ValueError('Wrong file type. Correct types: str, list')
    return dict(items)


# Subsitute templates
def prep_directories(folder_dict, string_replacement):
    """
    Replace string templates in folder dict.

    This function can be used to setup up dynamic folder paths and file list
    using string.Template.
    :params folder_dict: dict with folder path, file list pairs
    :type folder_dict: dict
    :params string_replacement: dict template, value pairs
    :type string_replacement: dict
    :return: resolved strings folder path, file list pairs
    :rtype: dict
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # Init variables
    new_folder_dict = dict()

    # Log replacements values
    logger.debug('String replacement value pairs: {0}'.format(string_replacement))

    # function routines
    for path, file_elem in folder_dict.items():
        logger.debug('Processing: {0}, {1}'.format(path, file_elem))
        new_path = Template(path).safe_substitute(**string_replacement)
        new_file_elem = [Template(i).safe_substitute(**string_replacement)
                         for i in file_elem]
        new_folder_dict[new_path] = new_file_elem
    return new_folder_dict


# Create folder structure
def create_directories(folder_dict, creation_root):
    """
    Create the folder paths in the specified root.

    :params folder_dict: dict with folder path, file list pairs
    :type folder_dict: dict
    :params creation_root: Root for the created paths
    :type creation_root: str
    :return created folder
    :rtype list
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # store created paths
    created_dirs = list()

    # function routines
    for path in folder_dict:
        full_path = os.path.join(creation_root, path)
        logger.debug('Processing: {0}'.format(full_path))
        try:
            os.makedirs(full_path)
            logger.info('Created: {0}'.format(full_path))
            created_dirs.append(full_path)
        except OSError:
            logger.exception('Failed to create: {0}'.format(full_path))
            # raise

    # Return
    return created_dirs


# Sub routines for file creation and copy
def copy_file(src, dst):
    """
    Subroutine for coping file object.

    :params src: file to copy
    :type src: str
    :params dst: destination path of the file
    :type dst: str
    :return: sucess
    :rtype: boolean
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # function routines
    try:
        shutil.copy2(src, dst)
        logger.info('Copied {0} to {1}'.format(src, dst))
        return True
    except OSError:
        logger.exception('Failed to copy: {0}'.format(src))
        return False


# Create the files listed as values
def create_files(folder_dict, creation_root):
    """
    Create the files listed in value of the folder keys

    :params folder_dict: dict with folder path, file list pairs
    :type folder_dict: dict
    :params creation_root:  Root for the created files
    :type creation_root: str
    :return created files
    :rtype list
    """
    # Init logger
    logger = logging.getLogger(__name__)

    # Store created files
    created_files = list()

    # function routines
    for path, files in folder_dict.items():
        full_path = os.path.join(creation_root, path)
        logger.debug('Processing folder: {0}'.format(full_path))

        # if a list of files
        if isinstance(files, list):
            # loop over the file list
            for file_elem in files:
                logger.debug('Processing file: {0}'.format(file_elem))

                # Check if the file elem is a path and exists
                if (len(file_elem.replace('\\', '/').split('/')) > 1
                        and not os.path.exists(file_elem)):
                    logger.debug('Does not exists: {0}'.format(file_elem))
                    continue

                # Check if it is a valid string and create an empty file object
                if isinstance(file_elem, basestring):
                    dst_path = os.path.join(full_path, file_elem)
                    with open(dst_path, 'w') as f:
                        f.write('')
                    logger.info('Created {0}'.format(dst_path))
                    created_files.append(dst_path)
                    continue

                # Get destination path
                dst_path = os.path.join(full_path, os.path.basename(file_elem))

                # Create the files
                result = copy_file(file_elem, dst_path)

                # Store created paths
                if result:
                    created_files.append(dst_path)

    # Return created files
    return created_files


# Main exec
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s: %(funcName)-20s] > %(levelname)-6s > %(message)s'
            )

    # Get input parameter
    args = sys.argv
    # Creation root
    assert os.path.isdir(os.path.abspath(args[1])), 'No valid creation root supplied!'
    creation_root = args[1]
    # Folder template dict
    assert (os.path.isfile(os.path.abspath(args[2]))
            and args[2].endswith('.json')), 'No valid json file supplied!'
    folder_json = args[2]
    # list of string replacements
    string_replacement = None
    if len(args) > 3:
        assert (os.path.isfile(os.path.abspath(args[3]))
                and args[3].endswith('.json')), 'No valid json string replacement supplied!'
        string_replacement = read_json(args[3])

    # Run preps
    folder_dict = read_json(folder_json)
    folder_dict = get_directories(folder_dict)
    if string_replacement:
        folder_dict = prep_directories(folder_dict, string_replacement)

    # Run creation
    create_directories(folder_dict, creation_root)

    create_files(folder_dict, creation_root)
