# Copyright 2024 CrackNuts. All rights reserved.

import configparser
import os

_user_config_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "config.ini")


def _get_user_config():
    _user_config = configparser.ConfigParser()
    if os.path.exists(_user_config_path):
        _user_config.read(_user_config_path)
    return _user_config


def save(user_config):
    with open(_user_config_path, "w") as f:
        user_config.write(f)


def get_option(key, fallback=None, section=None):
    if section is None:
        section, key = _get_section(key)
    return _get_user_config().get(section, key, fallback=fallback)


def set_option(key, value, section=None):
    _user_config = _get_user_config()
    if section is None:
        section, key = _get_section(key)
    if section is not None and section not in _user_config:
        _user_config.add_section(section)
    _user_config.set(section, key, value)
    save(_user_config)


def unset_option(key, section=None):
    _user_config = _get_user_config()
    if section is None:
        section, key = _get_section(key)
    if section in _user_config:
        _user_config.remove_option(section, key)

    section_options = _user_config.options(section)
    default_section_options = _user_config.defaults()
    section_options = [opt for opt in section_options if opt not in default_section_options]
    if len(section_options) == 0:
        _user_config.remove_section(section)
    save(_user_config)


def _get_section(key):
    if "." in key:
        section, key = key.split(".", 1)
        section = section.upper()
    else:
        section = "DEFAULT"

    return section, key
