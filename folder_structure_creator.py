#!/usr/bin/env python

"""
file=folder_structure_creator.py

Create a folder structure based on a dict.

Inputs:
1. <path>; path to creation root
2. <path>; json folder dict
3. <list>; dynamic values for string.template substition
"""


__author__ = 'Wilfried Pollan'


# Imports
import sys
import os
import json
import collections
import logging
from string import Template


# Read json folder template
def read_json(folder_dict):
    # Init logger
    logger = logging.getLogger(__name__)

    # function routines
    with open(folder_dict) as fobjs:
        logger.debug('Loading json: {0}'.format(folder_dict))
        return json.load(fobjs)


# Create dict with directories to create
def get_directories(d, parent_key=None):
    # Init logger
    logger = logging.getLogger(__name__)

    # Init variables
    sep = os.sep
    items = []

    # function routines
    for k, v in d.items():
        logger.debug('Processing: {0}, {1}'.format(k, v))
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(get_directories(v, parent_key=new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Subsitute templates
def prep_directories(folder_dict, string_replacement):
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
    # Init logger
    logger = logging.getLogger(__name__)

    # function routines
    for path in folder_dict:
        full_path = os.path.join(creation_root, path)
        logger.debug('Processing: {0}'.format(full_path))
        try:
            os.makedirs(full_path)
            logger.info('Created: {0}'.format(full_path))
        except OSError:
            logger.exception('Failed to create: {0}'.format(full_path))
            # raise


# Main exec
if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

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
