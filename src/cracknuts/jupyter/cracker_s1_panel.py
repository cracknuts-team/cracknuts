# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import typing
from typing import Any

from traitlets import traitlets

from cracknuts import logger
from cracknuts.cracker.cracker_s1 import CrackerS1, ConfigS1
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.ui_sync import ConfigProxy, observe_interceptor
import cracknuts.cracker.serial as serial


class CrackerS1PanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackerS1PanelWidget.js"
    _css = ""

    uri = traitlets.Unicode("cnp://192.168.0.11:8080").tag(sync=True)
    connect_status = traitlets.Bool(False).tag(sync=True)
    cracker_id = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_name = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_version = traitlets.Unicode("Unknown").tag(sync=True)

    # nut
    nut_enable = traitlets.Bool(False).tag(sync=True)
    nut_voltage = traitlets.Float(3.5).tag(sync=True)
    nut_clock_enable = traitlets.Bool(False).tag(sync=True)
    nut_clock = traitlets.Int(65000).tag(sync=True)

    nut_uart_enable = traitlets.Bool(False).tag(sync=True)
    nut_uart_baudrate = traitlets.Int(4).tag(sync=True)
    nut_uart_bytesize = traitlets.Int(8).tag(sync=True)
    nut_uart_parity = traitlets.Int(0).tag(sync=True)
    nut_uart_stopbits = traitlets.Int(0).tag(sync=True)

    nut_spi_enable = traitlets.Bool(False).tag(sync=True)
    nut_spi_speed = traitlets.Int(10_000).tag(sync=True)
    nut_spi_cpol = traitlets.Int(0).tag(sync=True)
    nut_spi_cpha = traitlets.Int(0).tag(sync=True)
    nut_spi_auto_select = traitlets.Bool(True).tag(sync=True)

    nut_i2c_enable = traitlets.Bool(False).tag(sync=True)
    nut_i2c_dev_addr = traitlets.Unicode("0x00").tag(sync=True)
    nut_i2c_speed = traitlets.Int(0).tag(sync=True)

    # osc
    osc_analog_channel_a_enable = traitlets.Bool(False).tag(sync=True)
    osc_analog_channel_b_enable = traitlets.Bool(True).tag(sync=True)
    sync_sample = traitlets.Bool(False).tag(sync=True)
    sync_args_times = traitlets.Int(1).tag(sync=True)

    osc_sample_rate = traitlets.Int(65000).tag(sync=True)
    osc_sample_phase = traitlets.Int(0).tag(sync=True)
    osc_sample_length = traitlets.Int(1024).tag(sync=True)
    osc_sample_delay = traitlets.Int(1024).tag(sync=True)

    osc_trigger_source = traitlets.Int(0).tag(sync=True)
    osc_trigger_mode = traitlets.Int(0).tag(sync=True)
    osc_trigger_edge = traitlets.Int(0).tag(sync=True)
    osc_trigger_edge_level = traitlets.Int(0).tag(sync=True)

    osc_analog_channel_a_gain = traitlets.Int(1).tag(sync=True)
    osc_analog_channel_b_gain = traitlets.Int(1).tag(sync=True)

    panel_config_different_from_cracker_config = traitlets.Bool(False).tag(sync=True)

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._logger = logger.get_logger(self)
        self._observe: bool = True
        self.cracker: CrackerS1 | None = None
        if "cracker" in kwargs:
            self.cracker: CrackerS1 = kwargs["cracker"]
        if self.cracker is None:
            raise ValueError("cracker is required")
        self.reg_msg_handler("connectButton", "onClick", self.msg_connection_button_on_click)
        self.connect_status = self.cracker.get_connection_status()
        if self.connect_status:
            _, self.cracker_id = self.cracker.get_id()
            _, self.cracker_name = self.cracker.get_hardware_model()
            # _, self.cracker_version = self.cracker.get_firmware_version()

    def read_config_from_cracker(self) -> None:
        # connection
        connect_uri = None
        if self.cracker.get_uri() is not None:
            connect_uri = self.cracker.get_uri()

        cracker_config = self.cracker.get_current_config()
        self.update_cracker_panel_config(cracker_config.__dict__, connect_uri)

    def write_config_to_cracker(self) -> None:
        self.cracker.write_config_to_cracker(self.get_cracker_panel_config())
        self.panel_config_different_from_cracker_config = False
        self.listen_cracker_config()

    def get_cracker_panel_config(self):
        panel_config = ConfigS1()
        self._logger.warning(f"xxxx {panel_config.__dict__.keys()}")
        for prop in panel_config.__dict__.keys():
            if hasattr(self, prop):
                self._logger.warning(f"Sett config {prop}: {getattr(self, prop)}")
                setattr(panel_config, prop, getattr(self, prop))
            else:
                self._logger.error(f"Failed to get configuration properties: the widget has no attribute named {prop}")
        return panel_config

    def update_cracker_panel_config(self, config: dict[str, object] | ConfigS1, connect_uri) -> None:
        """
        Sync cracker current to panel(Jupyter widget UI)
        """

        self._observe = False
        self.uri = connect_uri
        if isinstance(config, ConfigS1):
            config = config.__dict__
        for name, value in config.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                self._logger.error(
                    f"Failed to sync configuration to widget: the widget has no attribute named '{name}'."
                )
        self._observe = True

    def listen_cracker_config(self) -> None:
        """
        Bind the cracker and crackerPanel objects so that when the configuration of cracker is set,
        the updated values are automatically synchronized with panel through a ProxyConfig object.
        """
        proxy_config = ConfigProxy(self.cracker.get_current_config(), self)
        self.cracker._config = proxy_config

    def msg_connection_button_on_click(self, args: dict[str, typing.Any]):
        if args.get("action") == "connect":
            self.cracker.connect()
            if self.cracker.get_connection_status():
                self.connect_status = True
                _, self.cracker_id = self.cracker.get_id()
                _, self.cracker_name = self.cracker.get_hardware_model()
                # _, self.cracker_version = self.cracker.get_firmware_version()
            else:
                self.connect_status = False
        else:
            self.cracker.disconnect()
            self.connect_status = False
        self.send({"connectFinished": self.connect_status})

    @traitlets.observe("uri")
    @observe_interceptor
    def uri_on_changed(self, change):
        self.cracker.set_uri(change.get("new"))

    @traitlets.observe("nut_enable")
    @observe_interceptor
    def nut_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.nut_voltage_enable() if enabled else self.cracker.nut_voltage_disable()
        if enabled:
            self.cracker.nut_voltage(self.cracker.get_current_config().nut_voltage)

    @traitlets.observe("nut_voltage")
    @observe_interceptor
    def nut_voltage_changed(self, change):
        self._logger.error(f"nut voltage changed: {change.get('old')} - {change.get('new')}")
        self._logger.error(f"nut voltage changed: {change}")
        self.cracker.nut_voltage(change.get("new"))

    @traitlets.observe("nut_clock_enable")
    @observe_interceptor
    def nut_clock_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.nut_clock_enable() if enabled else self.cracker.nut_clock_disable()
        if enabled:
            self.cracker.nut_clock_freq(self.cracker.get_current_config().nut_clock)

    @traitlets.observe("nut_clock")
    @observe_interceptor
    def nut_clock_changed(self, change):
        self.cracker.nut_clock_freq(int(change.get("new")))

    @traitlets.observe("osc_sample_phase")
    @observe_interceptor
    def osc_sample_phase_changed(self, change):
        self.cracker.osc_sample_clock_phase(int(change.get("new")))

    @traitlets.observe("osc_sample_length")
    @observe_interceptor
    def osc_sample_len_changed(self, change):
        self.cracker.osc_sample_length(int(change.get("new")))

    @traitlets.observe("osc_sample_delay")
    @observe_interceptor
    def osc_sample_delay_changed(self, change):
        self.cracker.osc_sample_delay(int(change.get("new")))

    @traitlets.observe("osc_sample_rate")
    @observe_interceptor
    def osc_sample_rate_changed(self, change):
        self.cracker.osc_sample_clock(int(change.get("new")))

    @traitlets.observe("osc_analog_channel_a_enable")
    @observe_interceptor
    def osc_analog_channel_a_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.osc_analog_enable(0) if enabled else self.cracker.osc_analog_disable(0)
        if enabled:
            self.cracker.osc_analog_gain(0, self.cracker.get_current_config().osc_analog_channel_0_gain)

    @traitlets.observe("osc_analog_channel_b_enable")
    @observe_interceptor
    def osc_analog_channel_b_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.osc_analog_enable(1) if enabled else self.cracker.osc_analog_disable(1)
        if enabled:
            self.cracker.osc_analog_gain(1, self.cracker.get_current_config().osc_analog_channel_1_gain)

    @traitlets.observe("osc_trigger_source")
    @observe_interceptor
    def osc_trigger_source_changed(self, change):
        self.cracker.osc_trigger_source(change.get("new"))

    @traitlets.observe("osc_trigger_mode")
    @observe_interceptor
    def osc_trigger_mode_changed(self, change):
        self.cracker.osc_trigger_mode(change.get("new"))

    @traitlets.observe("osc_trigger_edge")
    @observe_interceptor
    def osc_trigger_edge_changed(self, change):
        self.cracker.osc_trigger_edge(change.get("new"))

    @traitlets.observe("osc_trigger_edge_level")
    @observe_interceptor
    def osc_trigger_edge_level_changed(self, change):
        self.cracker.osc_trigger_level(change.get("new"))

    @traitlets.observe("osc_analog_channel_a_gain", "osc_analog_channel_b_gain")
    @observe_interceptor
    def osc_analog_channel_gain_changed(self, change):
        name = change.get("name")
        channel = None
        if name == "osc_analog_channel_a_gain":
            channel = 0
        elif name == "osc_analog_channel_b_gain":
            channel = 1
        if channel is not None:
            self.cracker.osc_analog_gain(channel, change.get("new"))

    @traitlets.observe("nut_uart_enable")
    @observe_interceptor
    def nut_uart_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.uart_enable() if enabled else self.cracker.uart_disable()

        if enabled:
            self.cracker.uart_config(
                serial.Baudrate(self.nut_uart_baudrate),
                serial.Bytesize(self.nut_uart_bytesize),
                serial.Parity(self.nut_uart_parity),
                serial.Stopbits(self.nut_uart_stopbits),
            )

    @traitlets.observe("nut_uart_baudrate")
    @observe_interceptor
    def nut_uart_baudrate_changed(self, change):
        self.cracker.uart_config(
            serial.Baudrate(change.get("new")),
            serial.Bytesize(self.nut_uart_bytesize),
            serial.Parity(self.nut_uart_parity),
            serial.Stopbits(self.nut_uart_stopbits),
        )

    @traitlets.observe("nut_uart_bytesize")
    @observe_interceptor
    def nut_uart_bytesize_changed(self, change):
        self.cracker.uart_config(
            serial.Baudrate(self.nut_uart_baudrate),
            serial.Bytesize(change.get("new")),
            serial.Parity(self.nut_uart_parity),
            serial.Stopbits(self.nut_uart_stopbits),
        )

    @traitlets.observe("nut_uart_parity")
    @observe_interceptor
    def nut_uart_parity_changed(self, change):
        self.cracker.uart_config(
            serial.Baudrate(self.nut_uart_baudrate),
            serial.Bytesize(self.nut_uart_bytesize),
            serial.Parity(change.get("new")),
            serial.Stopbits(self.nut_uart_stopbits),
        )

    @traitlets.observe("nut_uart_stopbits")
    @observe_interceptor
    def nut_uart_stopbits_changed(self, change):
        self.cracker.uart_config(
            serial.Baudrate(self.nut_uart_baudrate),
            serial.Bytesize(self.nut_uart_bytesize),
            serial.Parity(self.nut_uart_parity),
            serial.Stopbits(change.get("new")),
        )

    @traitlets.observe("nut_spi_enable")
    @observe_interceptor
    def nut_spi_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.spi_enable() if enabled else self.cracker.spi_disable()
        if enabled:
            self.cracker.spi_config(
                self.nut_spi_speed,
                serial.SpiCpol(self.nut_spi_cpol),
                serial.SpiCpha(self.nut_spi_cpha),
                self.nut_spi_auto_select,
            )

    @traitlets.observe("nut_spi_speed")
    @observe_interceptor
    def nut_spi_speed_changed(self, change):
        self.cracker.spi_config(
            change.get("new"),
            serial.SpiCpol(self.nut_spi_cpol),
            serial.SpiCpha(self.nut_spi_cpha),
            self.nut_spi_auto_select,
        )

    @traitlets.observe("nut_spi_cpol")
    @observe_interceptor
    def nut_spi_cpol_changed(self, change):
        self.cracker.spi_config(
            self.nut_spi_speed,
            serial.SpiCpol(change.get("new")),
            serial.SpiCpha(self.nut_spi_cpha),
            self.nut_spi_auto_select,
        )

    @traitlets.observe("nut_spi_cpha")
    @observe_interceptor
    def nut_spi_cpha_changed(self, change):
        self.cracker.spi_config(
            self.nut_spi_speed,
            serial.SpiCpol(self.nut_spi_cpol),
            serial.SpiCpha(change.get("new")),
            self.nut_spi_auto_select,
        )

    @traitlets.observe("nut_spi_auto_select")
    @observe_interceptor
    def nut_spi_auto_select_changed(self, change):
        self.cracker.spi_config(
            self.nut_spi_speed, serial.SpiCpol(self.nut_spi_cpol), serial.SpiCpha(self.nut_spi_cpha), change.get("new")
        )

    @traitlets.observe("nut_i2c_enable")
    @observe_interceptor
    def nut_i2c_enable_changed(self, change):
        enabled = bool(change.get("new"))
        self.cracker.i2c_enable() if enabled else self.cracker.i2c_disable()
        if enabled:
            self.cracker.i2c_config(int(self.nut_i2c_dev_addr, 16), serial.I2cSpeed(self.nut_i2c_speed))

    @traitlets.observe("nut_i2c_dev_addr")
    @observe_interceptor
    def nut_i2c_dev_addr_changed(self, change):
        self.cracker.i2c_config(int(change.get("new"), 16), serial.I2cSpeed(self.nut_i2c_speed))

    @traitlets.observe("nut_i2c_speed")
    @observe_interceptor
    def nut_i2c_speed_changed(self, change):
        self.cracker.i2c_config(int(self.nut_i2c_dev_addr, 16), serial.I2cSpeed(change.get("new")))
