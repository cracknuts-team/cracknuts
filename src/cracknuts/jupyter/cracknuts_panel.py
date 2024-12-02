# Copyright 2024 CrackNuts. All rights reserved.

import json
import os
import pathlib
import typing
import sys

from cracknuts.cracker.stateful_cracker import StatefulCracker
from cracknuts.jupyter.acquisition_panel import AcquisitionPanelWidget
from cracknuts.jupyter.cracker_panel import CrackerPanelWidget
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.trace_panel import TraceMonitorPanelWidget


class CracknutsPanelWidget(CrackerPanelWidget, AcquisitionPanelWidget, TraceMonitorPanelWidget, MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackNutsPanelWidget.js"
    _css = ""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if "acquisition" not in kwargs:
            raise ValueError("acquisition must be provided")
        kwargs["cracker"]: StatefulCracker = kwargs["acquisition"].cracker
        super().__init__(*args, **kwargs)
        self._load_current_path_config()
        self.reg_msg_handler("dumpConfigButton", "onClick", self.dump_config_button_click)
        self.reg_msg_handler("loadConfigButton", "onClick", self.load_config_button_click)
        self.reg_msg_handler("saveConfigButton", "onClick", self.save_config_button_click)

    def sync_config(self) -> None:
        CrackerPanelWidget.sync_config(self)
        AcquisitionPanelWidget.sync_config(self)

    def bind(self) -> None:
        CrackerPanelWidget.bind(self)
        AcquisitionPanelWidget.bind(self)

    def dump_config_button_click(self, args: dict[str, typing.Any]):
        self.send({"dumpConfigCompleted": self._dump_config()})

    def load_config_button_click(self, args: dict[str, typing.Any]):
        connection_info = args.get("connection")
        config_info = args.get("config")
        acquisition_info = args.get("acquisition")
        self.cracker.load_config_from_str(config_info)
        self.cracker.set_uri(connection_info)
        self.acquisition.load_config_from_str(acquisition_info)
        self.sync_config()
        self.send({"loadConfigCompleted": True})

    def save_config_button_click(self, args: dict[str, typing.Any]):
        current_config_path = self._get_current_config_path()
        with open(current_config_path, "w") as f:
            f.write(self._dump_config())

    def _dump_config(self):
        return json.dumps(
            {
                "connection": self.cracker.get_uri(),
                "config": self.cracker.dump_config(),
                "acquisition": self.acquisition.dump_config(),
            }
        )

    def _load_current_path_config(self):
        """
        Load the workspace configuration if it exists.
        """
        current_config_path = self._get_current_config_path()

        if current_config_path is not None and os.path.exists(current_config_path):
            with open(current_config_path) as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError as e:
                    self._logger.error(f"Load workspace config file failed: {e.args}")
                    return
                connection_info = config.get("connection")
                config_info = config.get("config")
                acquisition_info = config.get("acquisition")
                self.cracker.load_config_from_str(config_info)
                self.cracker.set_uri(connection_info)
                self.acquisition.load_config_from_str(acquisition_info)
        else:
            self._logger.warning("Current config path is None or is no exist, current config will be ignored.")

    def _get_current_config_path(self):
        global_vars = sys.modules["__main__"].__dict__

        ipynb_path = None

        if "__vsc_ipynb_file__" in global_vars:
            ipynb_path = global_vars["__vsc_ipynb_file__"]
        elif "__session__" in global_vars:
            ipynb_path = global_vars["__session__"]

        if ipynb_path is not None:
            return os.path.join(os.path.dirname(ipynb_path), "." + os.path.basename(ipynb_path) + ".cncfg")
