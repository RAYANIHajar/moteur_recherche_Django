"""
@author: Mohammed Jassim
"""

import configparser
import os


def config(config_file_dir: list = None, config_file_name: str = None):
    """
    Config file parsing function
    :param config_file_name: file name, if it is None 'ENVIRONMENT' will be set as value
    :param config_file_dir: If none root working directory/config/config_env.ini file will be taken
    :return: object.get(tag,value) => to retrieve value
    """
    if config_file_name is None:
        environment = os.getenv('ENVIRONMENT')
        config_file_name = f"config_{environment}.ini"

    if config_file_dir:
        config_file_path = os.path.join(f'{os.sep}'.join(config_file_dir), config_file_name)

    else:
        config_file_path = os.path.join('config', config_file_name)

    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Missing config file {config_file_path}")

    config_obj = configparser.RawConfigParser()
    config_obj.read(config_file_path)

    return config_obj
