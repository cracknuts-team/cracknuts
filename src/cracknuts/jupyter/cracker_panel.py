# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import typing
from typing import Any

from traitlets import traitlets

from cracknuts import logger
from cracknuts.cracker.stateful_cracker import StatefulCracker
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.ui_sync import ConfigProxy, observe_interceptor


class CrackerPanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackerPanelWidget.js"
    _css = ""

    uri = traitlets.Unicode("cnp://192.168.0.11:8080").tag(sync=True)
    connect_status = traitlets.Bool(False).tag(sync=True)
    cracker_id = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_name = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_version = traitlets.Unicode("Unknown").tag(sync=True)

    # nut
    nut_enable = traitlets.Bool(False).tag(sync=True)
    nut_voltage = traitlets.Int(3300).tag(sync=True)
    nut_clock = traitlets.Float(62.5).tag(sync=True)

    # adc
    osc_analog_channel_a_enable = traitlets.Bool(False).tag(sync=True)
    osc_analog_channel_b_enable = traitlets.Bool(True).tag(sync=True)
    sync_sample = traitlets.Bool(False).tag(sync=True)
    sync_args_times = traitlets.Int(1).tag(sync=True)

    osc_sample_clock = traitlets.Float(62.5).tag(sync=True)
    osc_sample_phase = traitlets.Int(0).tag(sync=True)
    osc_sample_len = traitlets.Int(1024).tag(sync=True)
    osc_sample_delay = traitlets.Int(1024).tag(sync=True)

    osc_trigger_source = traitlets.Int(0).tag(sync=True)
    osc_trigger_mode = traitlets.Int(0).tag(sync=True)
    osc_trigger_edge = traitlets.Int(0).tag(sync=True)
    osc_trigger_edge_level = traitlets.Int(0).tag(sync=True)

    osc_analog_channel_a_gain = traitlets.Int(1).tag(sync=True)
    osc_analog_channel_b_gain = traitlets.Int(1).tag(sync=True)

    def __init__(self, *args: Any, **kwargs: Any):
        # todo optimize init param with specifically args and kwargs.
        super().__init__(*args, **kwargs)
        self._logger = logger.get_logger(self)
        self._observe: bool = True
        self.cracker: StatefulCracker | None = None
        if "cracker" in kwargs and isinstance(kwargs["cracker"], StatefulCracker):
            self.cracker: StatefulCracker = kwargs["cracker"]
        if self.cracker is None:
            raise ValueError("cracker is required")
        self.reg_msg_handler("connectButton", "onClick", self.msg_connection_button_on_click)

    def sync_config(self) -> None:
        """
        Sync cracker current to panel(Jupyter widget UI)
        """
        config = self.cracker.get_current_config()
        self._observe = False
        if self.cracker.get_uri() is not None:
            self.uri = self.cracker.get_uri()
        # nut
        if config.nut_enable is not None:
            self.nut_enable = config.nut_enable
        if config.nut_voltage is not None:
            self.nut_voltage = config.nut_voltage
        if config.nut_clock is not None:
            self.nut_clock = config.nut_clock / 1000
        # osc
        self.osc_analog_channel_a_enable = self.cracker.get_current_config().osc_analog_channel_enable.get(1, False)
        self.osc_analog_channel_b_enable = self.cracker.get_current_config().osc_analog_channel_enable.get(2, True)

        self._observe = True

    def bind(self) -> None:
        """
        Bind the cracker and crackerPanel objects so that when the configuration of cracker is set,
        the updated values are automatically synchronized with panel through a ProxyConfig object.
        """
        proxy_config = ConfigProxy(self.cracker.get_current_config(), self)
        self.cracker._config = proxy_config

        proxy_config.bind("nut_clock", formatter=lambda v: v / 1000)
        proxy_config.bind("osc_sample_clock", formatter=lambda v: v / 1000)
        # todo bind cracker config set event.

    def msg_connection_button_on_click(self, args: dict[str, typing.Any]):
        if args.get("action") == "connect":
            self.cracker.connect()
            if self.cracker.get_connection_status():
                self.connect_status = True
                self.cracker_id = self.cracker.get_id()
                self.cracker_name = self.cracker.get_name()
                self.cracker_version = self.cracker.get_version()
            else:
                self.connect_status = False
        else:
            self.cracker.disconnect()
            self.connect_status = False
        self.send({"connectFinished": self.connect_status})

    @traitlets.observe("uri")
    @observe_interceptor
    def uri_on_change(self, change):
        self.cracker.set_uri(change.get("new"))

    @traitlets.observe("nut_enable")
    @observe_interceptor
    def nut_enable_change(self, change):
        self.cracker.nut_enable(1 if change.get("new") else 0)

    @traitlets.observe("nut_voltage")
    @observe_interceptor
    def nut_voltage_change(self, change):
        self.cracker.nut_voltage(change.get("new"))

    @traitlets.observe("nut_clock")
    @observe_interceptor
    def _nut_clock_change(self, change):
        self.cracker.nut_clock(int(change.get("new") * 1000))

    @traitlets.observe("osc_sample_phase")
    @observe_interceptor
    def osc_sample_phase_change(self, change):
        self.cracker.osc_set_sample_phase(int(change.get("new")))

    @traitlets.observe("osc_sample_len")
    @observe_interceptor
    def osc_sample_len_change(self, change):
        self.cracker.osc_set_sample_len(int(change.get("new")))

    @traitlets.observe("osc_sample_delay")
    @observe_interceptor
    def osc_sample_delay_change(self, change):
        self.cracker.osc_set_sample_delay(int(change.get("new")))

    @traitlets.observe("osc_sample_clock")
    @observe_interceptor
    def osc_sample_clock_change(self, change):
        self.cracker.osc_set_sample_clock(int(change.get("new") * 1000))

    @traitlets.observe("osc_analog_channel_a_enable")
    @observe_interceptor
    def osc_analog_channel_a_enable_changed(self, change):
        self.cracker.osc_set_analog_channel_enable({1: change.get("new"), 2: self.osc_analog_channel_b_enable})

    @traitlets.observe("osc_analog_channel_b_enable")
    @observe_interceptor
    def osc_analog_channel_b_enable_changed(self, change):
        self.cracker.osc_set_analog_channel_enable({1: self.osc_analog_channel_a_enable, 2: change.get("new")})

    @traitlets.observe("osc_trigger_source")
    @observe_interceptor
    def osc_set_trigger_source(self, change):
        self.cracker.osc_set_analog_trigger_source(change.get("new"))

    @traitlets.observe("osc_trigger_mode")
    @observe_interceptor
    def osc_set_trigger_mode(self, change):
        self.cracker.osc_set_trigger_mode(change.get("new"))

    @traitlets.observe("osc_trigger_edge")
    @observe_interceptor
    def osc_set_trigger_edge(self, change):
        self.cracker.osc_set_trigger_edge(change.get("new"))

    @traitlets.observe("osc_trigger_edge_level")
    @observe_interceptor
    def osc_set_trigger_edge_level(self, change):
        self.cracker.osc_set_trigger_edge_level(change.get("new"))

    @traitlets.observe("osc_analog_channel_a_gain", "osc_analog_channel_b_gain")
    @observe_interceptor
    def osc_set_analog_channel_gain(self, change):
        name = change.get("name")
        channel = None
        if name == "osc_analog_channel_a_gain":
            channel = 1
        elif name == "osc_analog_channel_b_gain":
            channel = 2
        if channel is not None:
            self.cracker.osc_set_analog_gain(channel, change.get("new"))
