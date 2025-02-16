# Copyright 2024 CrackNuts. All rights reserved.

import configparser
import os

_user_config_path = os.path.join(os.path.expanduser("~"), ".cracknuts", "config.ini")
_user_config = configparser.ConfigParser()
if os.path.exists(_user_config_path):
    _user_config.read(_user_config_path)
if "GENERAL" not in _user_config:
    _user_config.add_section("GENERAL")


def save():
    with open(_user_config_path, "w") as f:
        _user_config.write(f)


def set_language(language):
    _user_config.set("GENERAL", "language", language)
    save()


def get_language():
    return _user_config.get("GENERAL", "language", fallback="en")
