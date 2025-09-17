import typing
from abc import ABC
from enum import Enum

from traitlets import traitlets

from cracknuts import CrackerS1
from cracknuts.cracker.cracker_s1 import ConfigS1
from cracknuts.jupyter.cracker.mixin.base_mixin import BaseMixin

DEFAULT_URI = "cnp://192.168.0.10:8080"


class Connection(BaseMixin, ABC):
    uri = traitlets.Unicode(DEFAULT_URI).tag(sync=True)
    connect_status = traitlets.Bool(False).tag(sync=True)
    cracker_id = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_name = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_version = traitlets.Unicode("Unknown").tag(sync=True)

    def __init__(self, cracker: CrackerS1):
        super().__init__()
        self.cracker: CrackerS1 = cracker
        self.reg_msg_handler("connectButton", "onClick", self.msg_connection_button_on_click)

    def msg_connection_button_on_click(self, args: dict[str, typing.Any]):
        if args.get("action") == "connect":
            self.cracker.connect()
            if self.cracker.get_connection_status():
                self.connect_status = True
                self._compare_config(cracker_config=self.cracker.get_current_config())
            else:
                self.connect_status = False
        else:
            self.cracker.disconnect()
            self.connect_status = False
        self.send({"connectFinished": self.connect_status})

    def _compare_config(self, cracker_config: ConfigS1):
        """
        Compare config between current configuration in panel and
        the configuration from cracker after connect from panel.

        """

        if self._has_connected_before:
            panel_cracker_config = self.get_cracker_panel_config().__dict__

            # uri = workspace_config.get("connection")
            if panel_cracker_config:
                for k, v in panel_cracker_config.items():
                    # Skip comparison for ignored configuration items.
                    if k in ("nut_timeout",):
                        continue
                    if hasattr(cracker_config, k):
                        cv = getattr(cracker_config, k)
                        if isinstance(cv, Enum):
                            cv = cv.value
                        if v != cv:
                            self.panel_config_different_from_cracker_config = True
                            self._logger.warning(
                                f"The configuration item {k} differs between the configuration file "
                                f"({v}) and the cracker ({cv})."
                            )
                            break
                    else:
                        self._logger.error(
                            f"Config has no attribute named {k}, "
                            f"which comes from the JSON key in the panel configuration."
                        )
                if not self.panel_config_different_from_cracker_config:
                    self.listen_cracker_config()
            else:
                self._logger.error(
                    "Configuration file format error: The cracker configuration segment is missing. "
                    "The configuration from the cracker or the default configuration will be used."
                )
                self.read_config_from_cracker()
                self.listen_cracker_config()
        else:
            self.read_config_from_cracker()
            self.listen_cracker_config()
