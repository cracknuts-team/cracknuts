import pathlib

from traitlets import traitlets

from cracknuts.jupyter.glitch_test_panel import GlitchTestPanel
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.utils import user_config


class CrackerG1Panel(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackerG1Widget.js"
    _css = ""

    uri = traitlets.Unicode("cnp://192.168.0.10:8080").tag(sync=True)
    connect_status = traitlets.Bool(False).tag(sync=True)
    cracker_id = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_name = traitlets.Unicode("Unknown").tag(sync=True)
    cracker_version = traitlets.Unicode("Unknown").tag(sync=True)

    # nut
    nut_enable = traitlets.Bool(False).tag(sync=True)
    nut_voltage = traitlets.Float(3.3).tag(sync=True)
    nut_clock_enable = traitlets.Bool(False).tag(sync=True)
    nut_clock = traitlets.Int(65000).tag(sync=True)
    nut_reset_io_enable = traitlets.Bool(False).tag(sync=True)

    nut_uart_enable = traitlets.Bool(False).tag(sync=True)
    nut_uart_baudrate = traitlets.Int(4).tag(sync=True)
    nut_uart_bytesize = traitlets.Int(8).tag(sync=True)
    nut_uart_parity = traitlets.Int(0).tag(sync=True)
    nut_uart_stopbits = traitlets.Int(0).tag(sync=True)

    nut_spi_enable = traitlets.Bool(False).tag(sync=True)
    nut_spi_speed = traitlets.Float(10_000.0).tag(sync=True)
    nut_spi_speed_error = traitlets.Unicode("").tag(sync=True)
    nut_spi_speed_has_error = traitlets.Bool(False).tag(sync=True)
    nut_spi_cpol = traitlets.Int(0).tag(sync=True)
    nut_spi_cpha = traitlets.Int(0).tag(sync=True)
    nut_spi_csn_auto = traitlets.Bool(True).tag(sync=True)
    nut_spi_csn_delay = traitlets.Bool(True).tag(sync=True)

    nut_i2c_enable = traitlets.Bool(False).tag(sync=True)
    nut_i2c_dev_addr = traitlets.Unicode("0x00").tag(sync=True)
    nut_i2c_speed = traitlets.Int(0).tag(sync=True)
    nut_i2c_stretch_enable = traitlets.Bool(False).tag(sync=True)

    language = traitlets.Unicode("en").tag(sync=True)

    series_data = traitlets.Dict({}).tag(sync=True)

    custom_y_range: dict[str, tuple[int, int]] = traitlets.Dict({"0": (0, 0), "1": (0, 0)}).tag(sync=True)
    y_range: dict[int, tuple[int, int]] = traitlets.Dict({0: (None, None), 1: (None, None)}).tag(sync=True)
    combine_y_range = traitlets.Bool(False).tag(sync=True)

    scope_status = traitlets.Int(0).tag(sync=True)
    monitor_status = traitlets.Bool(False).tag(sync=True)
    lock_scope_operation = traitlets.Bool(False).tag(sync=True)
    monitor_period = traitlets.Float(1.0).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = user_config.get_option("language", fallback="en")
        self.glitch_test_panel = GlitchTestPanel()
