# Copyright 2024 CrackNuts. All rights reserved.
import traceback
import typing

from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.ui_sync import observe_interceptor
from cracknuts.cracker.cracker_g1 import (CrackerG1, wave_4m, wave_8m, wave_10m, wave_16m, wave_20m, wave_40m, wave_80m,
                                          get_clock_from_wave_length)

class ConfigG1Glitch(MsgHandlerPanelWidget):

    glitch_vcc_normal = traitlets.Float(3.3).tag(sync=True)
    glitch_vcc_config_wait = traitlets.Int(1).tag(sync=True)
    glitch_vcc_config_level = traitlets.Float(3.3).tag(sync=True)
    glitch_vcc_config_count = traitlets.Int(1).tag(sync=True)
    glitch_vcc_config_delay = traitlets.Int(0).tag(sync=True)
    glitch_vcc_config_repeat = traitlets.Int(1).tag(sync=True)

    glitch_gnd_normal = traitlets.Float(0.0).tag(sync=True)
    glitch_gnd_config_wait = traitlets.Int(1).tag(sync=True)
    glitch_gnd_config_level = traitlets.Float(0.0).tag(sync=True)
    glitch_gnd_config_count = traitlets.Int(1).tag(sync=True)
    glitch_gnd_config_delay = traitlets.Int(0).tag(sync=True)
    glitch_gnd_config_repeat = traitlets.Int(1).tag(sync=True)

    _glitch_clock_embed_wave: dict[str, list[float]] = {
        "4M": wave_4m,
        "8M": wave_8m,
        "10M": wave_10m,
        "16M": wave_16m,
        "20M": wave_20m,
        "40M": wave_40m,
        "80M": wave_80m
    }
    # These two attributes are used to synchronize waveform related settings made in Python code with the Jupyter interface.
    _glitch_clock_wave_normal: list[float] = wave_8m
    _glitch_clock_config_wave_glitch: list[float] = wave_4m
    glitch_clock_normal_freq_items: list[dict[str, typing.Any]] = traitlets.List([{
        "name":  f"{name}-[{', '.join(map(str, wave))}]",
        "tooltip": f"[{', '.join(map(str, wave))}]",
        "wave": wave
    } for name, wave in _glitch_clock_embed_wave.items()]).tag(sync=True)
    glitch_clock_normal_selected_freq_item_idx: int = traitlets.Int(1).tag(sync=True) # default 8m
    glitch_clock_glitch_freq_items: list[dict[str, typing.Any]] = traitlets.List([{
        "name": f"{name}-[{', '.join(map(str, wave))}]",
        "tooltip": f"[{', '.join(map(str, wave))}]",
        "wave": wave
    } for name, wave in _glitch_clock_embed_wave.items()]).tag(sync=True)
    glitch_clock_glitch_selected_freq_item_idx: int = traitlets.Int(1).tag(sync=True) # default 8m

    @property
    def glitch_clock_wave_normal(self) -> list[float]:
        return self._glitch_clock_wave_normal

    @glitch_clock_wave_normal.setter
    def glitch_clock_wave_normal(self, value: list[float]) -> None:
        self._glitch_clock_wave_normal = value
        for idx, item in enumerate(self.glitch_clock_normal_freq_items):
            if value == item["wave"]:
                self.glitch_clock_normal_selected_freq_item_idx = idx
                break

    @property
    def glitch_clock_config_wave_glitch(self) -> list[float]:
        return self._glitch_clock_config_wave_glitch

    @glitch_clock_config_wave_glitch.setter
    def glitch_clock_config_wave_glitch(self, value: list[float]) -> None:
        for idx, item in enumerate(self.glitch_clock_glitch_freq_items):
            if value == item["wave"]:
                self.glitch_clock_glitch_selected_freq_item_idx = idx
                return
        self._glitch_clock_freq_add(value)

    glitch_clock_config_wait: int = traitlets.Int(1).tag(sync=True)
    glitch_clock_config_delay: int = traitlets.Int(0).tag(sync=True)
    glitch_clock_config_repeat: int = traitlets.Int(1).tag(sync=True)


    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.cracker: CrackerG1 = kwargs["cracker"]
        self.reg_msg_handler("glitchVCCForceButton", "onClick", self.glitch_vcc_force)
        self.reg_msg_handler("glitchGNDForceButton", "onClick", self.glitch_gnd_force)
        self.reg_msg_handler("glitchClockFreqAddButton", "onClick", self.glitch_clock_freq_add)
        self.reg_msg_handler("glitchClockForceButton", "onClick", self.glitch_clock_force)

    def glitch_vcc_force(self, args: dict[str, typing.Any]):
        self.cracker.glitch_vcc_force()

    def glitch_gnd_force(self, args: dict[str, typing.Any]):
        self.cracker.glitch_gnd_force()

    def glitch_clock_freq_add(self, args: dict[str, typing.Any]):
        if "wave" in args.keys():
            new_wave = args["wave"]
            self._glitch_clock_freq_add(new_wave)

    def glitch_clock_force(self, args: dict[str, typing.Any]):
        self.cracker.glitch_clock_force()

    def _glitch_clock_freq_add(self, new_wave):
        glitch_clock_freq_items = [item for item in self.glitch_clock_glitch_freq_items]
        glitch_clock_freq_items.append({
            "name": f"C-{len(glitch_clock_freq_items) - len(self._glitch_clock_embed_wave)}-[{", ".join(map(str, new_wave))}]",
            "tooltip": f"[{", ".join(map(str, new_wave))}]",
            "wave": new_wave
        })
        self.glitch_clock_glitch_freq_items = glitch_clock_freq_items
        self.glitch_clock_glitch_selected_freq_item_idx = len(glitch_clock_freq_items) - 1

    def glitch_clock_freq_selected(self, args: dict[str, typing.Any]):
        if "selected" in args.keys():
            selected_clock_freq_item_idx = args["selected"]
            selected_clock_freq_item = self.glitch_clock_glitch_freq_items[selected_clock_freq_item_idx]
            if selected_clock_freq_item:
                self.glitch_clock_config_wave_glitch = selected_clock_freq_item["wave"]
                self.cracker.glitch_clock_config(
                    wave=self.glitch_clock_config_wave_glitch,
                    wait=self.glitch_clock_config_wait,
                    delay=self.glitch_clock_config_delay,
                    repeat=self.glitch_clock_config_repeat
                )


    def get_glitch_clock_normal_freq(self):
        return get_clock_from_wave_length(len(self.glitch_clock_wave_normal))

    def get_glitch_clock_glitch_freq(self):
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
    def glitch_gnd_config_wait_changed(self, change):
        self.cracker.glitch_gnd_config(
            change.get("new"),
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_level")
    @observe_interceptor
    def glitch_gnd_config_level_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            change.get("new"),
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_count")
    @observe_interceptor
    def glitch_gnd_config_count_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            change.get("new"),
            self.glitch_gnd_config_delay,
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_delay")
    @observe_interceptor
    def glitch_gnd_config_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            change.get("new"),
            self.glitch_gnd_config_repeat,
        )

    @traitlets.observe("glitch_gnd_config_repeat")
    @observe_interceptor
    def glitch_gnd_config_repeat_changed(self, change):
        self.cracker.glitch_gnd_config(
            self.glitch_gnd_config_wait,
            self.glitch_gnd_config_level,
            self.glitch_gnd_config_count,
            self.glitch_gnd_config_delay,
            change.get("new"),
        )

    @traitlets.observe("glitch_clock_config_wait")
    @observe_interceptor
    def glitch_clock_config_wait_changed(self, change):
        self.cracker.glitch_clock_config(
            wave=self._glitch_clock_config_wave_glitch,
            wait=change.get("new"),
            delay=self.glitch_clock_config_delay,
            repeat=self.glitch_clock_config_repeat,
        )

    @traitlets.observe("glitch_clock_config_delay")
    @observe_interceptor
    def glitch_clock_config_delay_changed(self, change):
        self.cracker.glitch_clock_config(
            wave=self._glitch_clock_config_wave_glitch,
            wait=self.glitch_clock_config_wait,
            delay=change.get("new"),
            repeat=self.glitch_clock_config_repeat,
        )

    @traitlets.observe("glitch_clock_config_repeat")
    @observe_interceptor
    def glitch_clock_config_repeat_changed(self, change):
        self.cracker.glitch_clock_config(
            wave=self._glitch_clock_config_wave_glitch,
            wait=self.glitch_clock_config_wait,
            delay=self.glitch_clock_config_delay,
            repeat=change.get("new"),
        )

    @traitlets.observe("glitch_clock_glitch_selected_freq_item_idx")
    @observe_interceptor
    def glitch_clock_glitch_selected_freq_item_idx_changed(self, change):
        self._glitch_clock_config_wave_glitch = self.glitch_clock_glitch_freq_items[change.get("new")]["wave"]
        self.cracker.glitch_clock_config(
            wave=self._glitch_clock_config_wave_glitch,
            wait=self.glitch_clock_config_wait,
            delay=self.glitch_clock_config_delay,
            repeat=self.glitch_clock_config_repeat,
        )