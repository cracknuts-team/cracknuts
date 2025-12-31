# Copyright 2024 CrackNuts. All rights reserved.

import typing

from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.ui_sync import observe_interceptor
from cracknuts.cracker.cracker_g1 import (CrackerG1, wave_4m, wave_8m, wave_10m, wave_16m, wave_20m, wave_40m, wave_80m,
                                          get_clock_from_wave_length)

class ConfigG1Glitch(MsgHandlerPanelWidget):

    glitch_vcc_normal = traitlets.Float(3.3).tag(sync=True)
    glitch_vcc_config_wait = traitlets.Int(0).tag(sync=True)
    glitch_vcc_config_level = traitlets.Float(0.0).tag(sync=True)
    glitch_vcc_config_count = traitlets.Int(1).tag(sync=True)
    glitch_vcc_config_delay = traitlets.Int(0).tag(sync=True)
    glitch_vcc_config_repeat = traitlets.Int(1).tag(sync=True)

    glitch_gnd_normal = traitlets.Float(0.0).tag(sync=True)
    glitch_gnd_config_wait = traitlets.Int(0).tag(sync=True)
    glitch_gnd_config_level = traitlets.Float(0.0).tag(sync=True)
    glitch_gnd_config_count = traitlets.Int(1).tag(sync=True)
    glitch_gnd_config_delay = traitlets.Int(0).tag(sync=True)
    glitch_gnd_config_repeat = traitlets.Int(1).tag(sync=True)

    glitch_clock_rate = traitlets.Unicode("8M").tag(sync=True) # for UI selection only
    glitch_clock_wave_normal: list[float] = traitlets.List([
        3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]).tag(sync=True)
    glitch_clock_config_wave_glitch: list[float] = traitlets.List([
        3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]).tag(sync=True)
    glitch_clock_config_wait: int = traitlets.Int(1)
    glitch_clock_config_count: int = traitlets.Int(2)
    glitch_clock_config_delay: int = traitlets.Int(2)
    glitch_clock_config_repeat: int = traitlets.Int(1)
    glitch_clock_enable: bool = traitlets.Bool(True)

    glitch_clock_embed_wave: dict[str, list[float]] = {
        "4M": wave_4m,
        "8M": wave_8m,
        "10M": wave_10m,
        "16M": wave_16m,
        "20M": wave_20m,
        "40M": wave_40m,
        "80M": wave_80m
    }


    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.cracker: CrackerG1 = kwargs["cracker"]
        self.reg_msg_handler("glitchVCCForceButton", "onClick", self.glitch_vcc_force)

    def glitch_vcc_force(self, args: dict[str, typing.Any]):
        self.cracker.glitch_vcc_force()

    def get_glitch_clock_normal_rate(self):
        return get_clock_from_wave_length(len(self.glitch_clock_wave_normal))

    def get_glitch_clock_glitch_rate(self):
        return get_clock_from_wave_length(len(self.glitch_clock_config_wave_glitch))

    @traitlets.observe("glitch_vcc_normal")
    @observe_interceptor
    def glitch_vcc_normal_changed(self, change):
        self.cracker.glitch_vcc_normal(change.get("new"))

    @traitlets.observe("glitch_vcc_config_level")
    @observe_interceptor
    def glitch_vcc_config_level_changed(self, change):
        self.cracker.glitch_vcc_config(
            self.glitch_vcc_config_wait,
            change.get("new"),
            self.glitch_vcc_config_count,
            self.glitch_vcc_config_delay,
            self.glitch_vcc_config_repeat,
        )

    @traitlets.observe("glitch_vcc_config_wait")
    @observe_interceptor
    def glitch_vcc_config_wait_changed(self, change):
        self.cracker.glitch_vcc_config(
            change.get("new"),
            self.glitch_vcc_config_level,
            self.glitch_vcc_config_count,
            self.glitch_vcc_config_delay,
            self.glitch_vcc_config_repeat,
        )

    @traitlets.observe("glitch_vcc_config_count")
    @observe_interceptor
    def glitch_vcc_config_count_changed(self, change):
        self.cracker.glitch_vcc_config(
            self.glitch_vcc_config_wait,
            self.glitch_vcc_config_level,
            change.get("new"),
            self.glitch_vcc_config_delay,
            self.glitch_vcc_config_repeat,
        )

    @traitlets.observe("glitch_vcc_config_repeat")
    @observe_interceptor
    def glitch_vcc_config_repeat_changed(self, change):
        self.cracker.glitch_vcc_config(
            self.glitch_vcc_config_wait,
            self.glitch_vcc_config_level,
            self.glitch_vcc_config_count,
            self.glitch_vcc_config_delay,
            change.get("new"),
        )

    @traitlets.observe("glitch_vcc_config_delay")
    @observe_interceptor
    def glitch_vcc_config_delay_changed(self, change):
        self.cracker.glitch_vcc_config(
            self.glitch_vcc_config_wait,
            self.glitch_vcc_config_level,
            self.glitch_vcc_config_count,
            change.get("new"),
            self.glitch_vcc_config_repeat,
        )

    @traitlets.observe("glitch_gnd_normal")
    @observe_interceptor
    def glitch_gnd_normal_changed(self, change):
        self.cracker.glitch_gnd_normal(change.get("new"))

    @traitlets.observe("glitch_gnd_config_wait")
    @observe_interceptor
    def glitch_gnd_glitch_voltage_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            change.get("new"),
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_count")
    @observe_interceptor
    def glitch_gnd_wait_changed(self, change):
        self.cracker.glitch_gnd_config(
            change.get("new"),
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_delay")
    @observe_interceptor
    def glitch_gnd_count_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            change.get("new"),
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_repeat")
    @observe_interceptor
    def glitch_gnd_repeat_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            change.get("new"),
        )

    @traitlets.observe("glitch_gnd_config_delay")
    @observe_interceptor
    def glitch_gnd_delay_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            change.get("new"),
            self.glitch_gnd_config_repeat,
        )
