# Copyright 2024 CrackNuts. All rights reserved.

import pathlib

import traitlets
from anywidget import AnyWidget

from cracknuts import logger
from cracknuts.glitch.param_generator import VCCGlitchParamGenerator, GlitchGenerateParam


class GlitchTestPanel(AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "GlitchTestPanelWidget.js"
    _css = ""

    tl_vcc_glitch_param_generator = traitlets.Dict({}).tag(sync=True)

    def __init__(self):
        super().__init__()
        self._logger = logger.get_logger(self)
        self._vcc_glitch_param_generator: VCCGlitchParamGenerator | None = None

    @traitlets.observe("vcc_glitch_param_generator")
    def on_vcc_glitch_param_change(self, change):
        vcc_glitch_param_generator_dict = change["new"]
        for param_type, param_dict in vcc_glitch_param_generator_dict.items():
            param = GlitchGenerateParam(**param_dict)
            param_type = param_type.lower()
            if param_type == "normal":
                self._vcc_glitch_param_generator.normal = param
            elif param_type == "glitch":
                self._vcc_glitch_param_generator.glitch = param
            elif param_type == "wait":
                self._vcc_glitch_param_generator.wait = param
            elif param_type == "count":
                self._vcc_glitch_param_generator.count = param
            elif param_type == "repeat":
                self._vcc_glitch_param_generator.repeat = param
            elif param_type == "interval":
                self._vcc_glitch_param_generator.interval = param
