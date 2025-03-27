# Copyright 2024 CrackNuts. All rights reserved.

import json
import os
import pathlib
import sys
import typing

import traitlets

from cracknuts.cracker.cracker_g1 import CrackerG1
from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.jupyter.acquisition_panel import AcquisitionPanelWidget
from cracknuts.jupyter.cracker_s1_panel import CrackerS1PanelWidget
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.scope_panel import ScopePanelWidget
from cracknuts.utils import user_config


class CracknutsPanelWidget(CrackerS1PanelWidget, AcquisitionPanelWidget, ScopePanelWidget, MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackNutsPanelWidget.js"
    _css = ""

    cracker_model = traitlets.Unicode("s1").tag(sync=True)
    language = traitlets.Unicode("en").tag(sync=True)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if "acquisition" not in kwargs:
            raise ValueError("acquisition must be provided")
        cracker = kwargs["acquisition"].cracker
        kwargs["cracker"] = cracker
        if isinstance(cracker, CrackerS1):
            self.cracker_model = "s1"
        elif isinstance(cracker, CrackerG1):
            self.cracker_model = "g1"
        else:
            raise ValueError(f"can't find panel for cracker type: {type(cracker)}.")
        super().__init__(*args, **kwargs)
        self.language = user_config.get_option("language", fallback="en")
        # self._load_current_path_config()
        workspace_config = self._get_workspace_config()
        if workspace_config:
            config_file_cracker_config = workspace_config.get("cracker")
            # uri = workspace_config.get("connection")
            uri = cracker.get_uri()
            cracker_config = cracker.get_current_config()
            if config_file_cracker_config:
                for k, v in config_file_cracker_config.items():
                    if hasattr(cracker_config, k):
                        cv = getattr(cracker_config, k)
                        if v != cv:
                            self.panel_config_different_from_cracker_config = True
                            break
                    else:
                        self._logger.error(
                            f"Config has no attribute named {k}, " f"which comes from the JSON key in the config file."
                        )
                if not self.panel_config_different_from_cracker_config:
                    self.listen_cracker_config()
                self.update_cracker_panel_config(config_file_cracker_config, uri)
            else:
                self._logger.error(
                    "Configuration file format error: The cracker configuration segment is missing. "
                    "The configuration from the cracker or the default configuration will be used."
                )
                self.read_config_from_cracker()
                self.listen_cracker_config()

            acquisition_config = workspace_config.get("acquisition")
            if acquisition_config:
                self.acquisition.load_config_from_json(workspace_config.get("acquisition"))
            else:
                self._logger.error(
                    "Configuration file format error: Acquisition configuration segment is missing. "
                    "The configuration from the acquisition object or "
                    "the default configuration will be used."
                )
            self.sync_config_from_acquisition()
            self.listen_acquisition_config()
        else:
            self.read_config_from_cracker()
            self.listen_cracker_config()
            self.sync_config_from_acquisition()
            self.listen_acquisition_config()

        self.reg_msg_handler("dumpConfigButton", "onClick", self.dump_config_button_click)
        self.reg_msg_handler("loadConfigButton", "onClick", self.load_config_button_click)
        self.reg_msg_handler("saveConfigButton", "onClick", self.save_config_button_click)
        self.reg_msg_handler("writeConfigButton", "onClick", self.write_config_button_click)
        self.reg_msg_handler("readConfigButton", "onClick", self.read_config_button_click)

    # def sync_config(self) -> None:
    #     self.read_config_from_cracker()
    #     self.sync_config_from_acquisition()
    #
    # def listen_config(self) -> None:
    #     self.listen_cracker_config()
    #     self.listen_acquisition_config()

    def dump_config_button_click(self, args: dict[str, typing.Any]):
        self.send({"dumpConfigCompleted": self._dump_config()})

    def load_config_button_click(self, args: dict[str, typing.Any]):
        connection_info = args.get("connection")
        config_info = args.get("cracker")
        acquisition_info = args.get("acquisition")
        self.cracker.load_config_from_str(config_info)
        self.cracker.set_uri(connection_info)
        self.acquisition.load_config_from_str(acquisition_info)
        self.read_config_from_cracker()
        self.send({"loadConfigCompleted": True})

    def write_config_button_click(self, args: dict[str, typing.Any]):
        self.write_config_to_cracker()

    def read_config_button_click(self, args: dict[str, typing.Any]):
        self.read_config_from_cracker()

    def save_config_button_click(self, args: dict[str, typing.Any]):
        current_config_path = self._get_workspace_config_path()
        self._logger.error(current_config_path)
        with open(current_config_path, "w") as f:
            self._logger.error(self._dump_config())
            f.write(self._dump_config())

    def _dump_config(self):
        return json.dumps(
            {
                "connection": self.cracker.get_uri(),
                "cracker": json.loads(self.cracker.dump_config()),
                "acquisition": json.loads(self.acquisition.dump_config()),
            },
            indent=4,
        )

    def _load_current_path_config(self):
        """
        Load the workspace configuration if it exists.
        """
        config = self._get_workspace_config()

        if config is not None:
            connection_info = config.get("connection")
            config_info = config.get("cracker")
            acquisition_info = config.get("acquisition")

            self.cracker.load_config_from_str(config_info)
            self.cracker.set_uri(connection_info)
            self.acquisition.load_config_from_str(acquisition_info)
        else:
            self._logger.debug("Current config path is None or is no exist, current config will be ignored.")

    def _get_workspace_config(self):
        current_config_path = self._get_workspace_config_path()
        if current_config_path is not None and os.path.exists(current_config_path):
            with open(current_config_path) as f:
                try:
                    config = json.load(f)
                    return config
                except json.JSONDecodeError as e:
                    self._logger.error(f"Load workspace config file failed: {e.args}")
                    return None

    @staticmethod
    def _get_workspace_config_path():
        global_vars = sys.modules["__main__"].__dict__

        ipynb_path = None

        if "__vsc_ipynb_file__" in global_vars:
            ipynb_path = global_vars["__vsc_ipynb_file__"]
        elif "__session__" in global_vars:
            ipynb_path = global_vars["__session__"]

        if ipynb_path is not None:
            return os.path.join(os.path.dirname(ipynb_path), "." + os.path.basename(ipynb_path)[:-6] + ".cncfg")

    @traitlets.observe("language")
    def on_language_change(self, change):
        user_config.set_option("language", change["new"])
