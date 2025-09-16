from cracknuts.jupyter.glitch_test_panel import GlitchTestPanel
from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class CrackerG1Panel(MsgHandlerPanelWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.glitch_test_panel = GlitchTestPanel()
