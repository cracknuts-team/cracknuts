# Copyright 2024 CrackNuts. All rights reserved.
import typing
from typing import Any

from traitlets import traitlets

from cracknuts.cracker.cracker_g1 import ConfigG1, CrackerG1
from cracknuts.jupyter.config.config_glitch import ConfigG1Glitch
from cracknuts.jupyter.cracker_s1_panel import CrackerPanelWidget
from cracknuts.jupyter.ui_sync import observe_interceptor


class CrackerG1Panel(CrackerPanelWidget, ConfigG1Glitch):

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.cracker: CrackerG1 = self.cracker

    def get_cracker_panel_config(self) -> ConfigG1:
        """
        Get the current configuration from panel(Jupyter widget UI)

        The nut_glitch_vcc_normal is mapped to nut_voltage,
        and nut_glitch_clock_enable is mapped to nut_clock_enable.

        """
        s1_panel_config = super().get_cracker_panel_config()
        panel_config = ConfigG1()
        for k, v in s1_panel_config.__dict__.items():
            setattr(panel_config, k, v)
        panel_config.glitch_vcc_normal = self.nut_voltage  # use nut_voltage as glitch_vcc_normal
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

        # Use glitch_clock_normal_rate as nut_clock. This field is ignored in the Jupyter UI,
        # but in a pure Python environment, users can read the nut clock configuration from it.
        panel_config.nut_clock = self.get_glitch_clock_normal_rate()
        panel_config.glitch_clock_len_normal = len(self.glitch_clock_wave_normal)
        panel_config.glitch_clock_wave_normal = self.glitch_clock_wave_normal
        panel_config.glitch_clock_len_glitch = len(self.glitch_clock_config_wave_glitch)
        panel_config.glitch_clock_wave_glitch = self.glitch_clock_config_wave_glitch
        panel_config.glitch_clock_config_wait = self.glitch_clock_config_wait
        panel_config.glitch_clock_config_count = self.glitch_clock_config_count
        panel_config.glitch_clock_config_delay = self.glitch_clock_config_delay
        panel_config.glitch_clock_config_repeat = self.glitch_clock_config_repeat
        panel_config.glitch_clock_enable = self.nut_clock_enable # use nut_clock_enable as glitch_clock_enable

        return panel_config

    def _panel_config_item_process(self, name: str, value: object) -> object:
        """
        Process a single panel configuration item:
        return the corresponding value when no extra processing is needed,
        or return None to indicate that the item is skipped or already processed by this function.
        """
        if name == "nut_voltage":
            return None # ignore, and use glitch_vcc_normal instead
        elif name == "nut_clock":
            return None # ignore, and use glitch_clock_normal_rate instead
        elif name == "nut_clock_enable":
            return None # ignore, and use glitch_clock_enable instead
        elif name == "glitch_vcc_normal":
            self.glitch_vcc_normal = value
            self.nut_voltage = value
            return None
        elif name == "glitch_clock_wave_normal":
            self.glitch_clock_wave_normal = typing.cast(list[int], value)
            self.nut_clock = self.get_glitch_clock_normal_rate()
            self.glitch_clock_rate = f"{round(self.nut_clock / 1000, 2)}M"
        elif name == "glitch_clock_enable":
            self.glitch_clock_enable = typing.cast(bool, value)
            self.nut_clock_enable = self.glitch_clock_enable
        elif name == "glitch_clock_len_normal":
            return None # ignore, already processed by glitch_clock_wave_normal
        elif name == "glitch_clock_config_len_glitch":
            return None # ignore, already processed by glitch_clock_wave_glitch
        elif name == "glitch_clock_config_wave_glitch":
            self.glitch_clock_config_wave_glitch = typing.cast(list[int], value)
            self.nut_clock = self.get_glitch_clock_normal_rate()
            self.glitch_clock_rate = f"{round(self.nut_clock / 1000, 2)}M"
        elif name in ("glitch_vcc_arm", "glitch_gnd_arm", "glitch_clock_arm"):
            return None # ignore these arm settings in G1 panel
        else:
            value = super()._panel_config_item_process(name, value)
        return value

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