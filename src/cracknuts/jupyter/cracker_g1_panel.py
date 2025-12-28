# Copyright 2024 CrackNuts. All rights reserved.

from typing import Any

from traitlets import traitlets

from cracknuts.cracker.cracker_g1 import ConfigG1
from cracknuts.jupyter.config.config_glitch import ConfigG1Glitch
from cracknuts.jupyter.cracker_s1_panel import CrackerPanelWidget
from cracknuts.jupyter.ui_sync import observe_interceptor


class CrackerG1Panel(CrackerPanelWidget, ConfigG1Glitch):

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def get_cracker_panel_config(self) -> ConfigG1:
        s1_panel_config = super().get_cracker_panel_config()
        panel_config = ConfigG1()
        for k, v in s1_panel_config.__dict__.items():
            setattr(panel_config, k, v)
        panel_config.glitch_vcc_normal = self.glitch_vcc_normal
        panel_config.glitch_vcc_config_wait = self.glitch_vcc_config_wait
        panel_config.glitch_vcc_config_level = self.glitch_vcc_config_level
        panel_config.glitch_vcc_config_count = self.glitch_vcc_config_count
        panel_config.glitch_vcc_config_delay = self.glitch_vcc_config_delay
        panel_config.glitch_vcc_config_repeat = self.glitch_vcc_config_repeat
        panel_config.glitch_gnd_normal = self.glitch_gnd_normal
        panel_config.glitch_gnd_config_wait = self.glitch_gnd_config_wait
        panel_config.glitch_gnd_config_level = self.glitch_gnd_config_level
        panel_config.glitch_gnd_config_count = self.glitch_gnd_config_count
        panel_config.glitch_gnd_config_delay = self.glitch_gnd_config_delay
        panel_config.glitch_gnd_config_repeat = self.glitch_gnd_config_repeat

        return panel_config

    def write_config_to_cracker(self) -> None:
        super().write_config_to_cracker()

    @traitlets.observe("nut_voltage")
    @observe_interceptor
    def nut_voltage_changed(self, change):
        self.cracker.nut_voltage(change.get("new"))

    @traitlets.observe("nut_clock")
    @observe_interceptor
    def nut_clock_changed(self, change):
        super().nut_clock_changed(change)

    @traitlets.observe("glitch_vcc_normal")
    @observe_interceptor
    def glitch_vcc_normal_changed(self, change):
        self.cracker.glitch_vcc_normal(change.get("new"))

    # TODO 这里有个同步的问题，就是电压和时钟实际上在界面中有两个位置（基本设置和故障注入），需要同步更新