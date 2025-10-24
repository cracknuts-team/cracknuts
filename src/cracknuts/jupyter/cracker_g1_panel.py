import json
import os
import pathlib
import sys
import typing
from enum import Enum

from traitlets import traitlets

from cracknuts import Acquisition, CrackerG1, logger
from cracknuts.acquisition.glitch_acquisition import GlitchAcquisition, GlitchDoData, GlitchAcquisitionBuilder
from cracknuts.jupyter.cracker_s1_panel import CrackerPanelWidget
from cracknuts.jupyter.acquisition_panel import GlitchAcquisitionPanelWidget
from cracknuts.jupyter.scope_panel import ScopePanelWidget
from cracknuts.jupyter.glitch_test_panel import GlitchTestPanel
from cracknuts.jupyter.panel import MsgHandlerPanelWidget
from cracknuts.jupyter.ui_sync import observe_interceptor
from cracknuts.utils import user_config


class CrackerConfigG1GlitchPanel(MsgHandlerPanelWidget):
    # glitch
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

    glitch_vcc_arm = False
    # glitch_vcc_config_wait = 0
    # glitch_vcc_config_level = 0
    # glitch_vcc_config_count = 0
    # glitch_vcc_config_delay = 0
    # glitch_vcc_config_repeat = 0
    # glitch_vcc_normal = 0
    glitch_gnd_arm = False
    # glitch_gnd_config_wait = 0
    # glitch_gnd_config_level = 0
    # glitch_gnd_config_count = 0
    # glitch_gnd_config_delay = 0
    # glitch_gnd_config_repeat = 0
    # glitch_gnd_normal = 0
    glitch_clock_arm = False
    glitch_clock_len_normal = 0
    glitch_clock_wave_normal = 0
    glitch_clock_config_len_glitch = 0
    glitch_clock_config_wave_glitch = 0
    glitch_clock_config_count = 0
    glitch_clock_config_delay = 0
    glitch_clock_config_repeat = 0
    glitch_clock_normal = 0

    # glitch test
    # glitch_test_params = traitlets.Dict({}).tag(sync=True)

    def __init__(self, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.cracker: CrackerG1 = kwargs["cracker"]
        self.reg_msg_handler("glitchVCCForceButton", "onClick", self.glitch_vcc_force)

    def glitch_vcc_force(self, args: dict[str, typing.Any]):
        self.cracker.glitch_vcc_force()

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


class CrackerG1Panel(
    CrackerPanelWidget,
    CrackerConfigG1GlitchPanel,
    GlitchAcquisitionPanelWidget,
    ScopePanelWidget,
    MsgHandlerPanelWidget,
):
    _esm = pathlib.Path(__file__).parent / "static" / "CrackerG1Widget.js"
    _css = ""

    language = traitlets.Unicode("en").tag(sync=True)

    glitch_test_params = traitlets.Dict({}).tag(sync=True)

    def __init__(self, cracker: CrackerG1, acquisition: GlitchAcquisition):
        super().__init__(**{"cracker": cracker, "acquisition": acquisition})
        self._logger = logger.get_logger(self)

        self.language = user_config.get_option("language", fallback="en")
        self.glitch_test_panel = GlitchTestPanel()

        self.cracker: CrackerG1 = cracker
        self.acquisition: GlitchAcquisition = acquisition

        self.uri = self.cracker.get_uri()
        self.language = user_config.get_option("language", fallback="en")

        if self.cracker.get_connection_status():
            self._has_connected_before = True
            workspace_config = self._get_workspace_config()
            if workspace_config:
                config_file_cracker_config = workspace_config.get("cracker")
                # uri = workspace_config.get("connection")
                uri = cracker.get_uri()
                cracker_config = cracker.get_current_config()
                if cracker_config is not None:
                    if config_file_cracker_config:
                        for k, v in config_file_cracker_config.items():
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
                                    f"which comes from the JSON key in the config file."
                                )
                        if not self.panel_config_different_from_cracker_config:
                            self.listen_cracker_config()
                        self.update_cracker_panel_config(config_file_cracker_config, uri)
                    else:
                        self._logger.error(
                            "Configuration file format error: The cracker configuration segment is missing. "
                            "The configuration from the cracker or the default configuration will be used."
                        )
                        self.read_config_from_cracker()
                        self.listen_cracker_config()
                else:
                    self.update_cracker_panel_config(config_file_cracker_config, uri)

                acquisition_config = workspace_config.get("acquisition")
                if acquisition_config:
                    self.acquisition.load_config_from_json(workspace_config.get("acquisition"))
                else:
                    self._logger.error(
                        "Configuration file format error: Acquisition configuration segment is missing. "
                        "The configuration from the acquisition object or "
                        "the default configuration will be used."
                    )
                self.sync_config_from_acquisition()
                self.listen_acquisition_config()
            else:
                self.read_config_from_cracker()
                self.listen_cracker_config()
                self.sync_config_from_acquisition()
                self.listen_acquisition_config()

        self.reg_msg_handler("dumpConfigButton", "onClick", self.dump_config_button_click)
        self.reg_msg_handler("loadConfigButton", "onClick", self.load_config_button_click)
        self.reg_msg_handler("saveConfigButton", "onClick", self.save_config_button_click)
        self.reg_msg_handler("writeConfigButton", "onClick", self.write_config_button_click)
        self.reg_msg_handler("readConfigButton", "onClick", self.read_config_button_click)

    def before_test(self):
        self.write_config_to_cracker()

    def before_run(self):
        self.write_config_to_cracker()

    def dump_config_button_click(self, args: dict[str, typing.Any]):
        self.send({"dumpConfigCompleted": self._dump_config()})

    def load_config_button_click(self, args: dict[str, typing.Any]):
        connection_info = args.get("connection")
        config_file_cracker_config = args.get("cracker")
        acquisition_info = args.get("acquisition")
        cracker_config = self.cracker.get_current_config()
        for k, v in config_file_cracker_config.items():
            if hasattr(cracker_config, k):
                cv = getattr(cracker_config, k)
                if isinstance(cv, Enum):
                    cv = cv.value
                if v != cv:
                    self.panel_config_different_from_cracker_config = True
                    self._logger.error(
                        f"The configuration item {k} differs between the configuration file "
                        f"({v}) and the cracker ({cv})."
                    )
                    break
            else:
                self._logger.error(
                    f"Config has no attribute named {k}, " f"which comes from the JSON key in the config file."
                )

        if self.panel_config_different_from_cracker_config:
            self.stop_listen_cracker_config()
            self.update_cracker_panel_config(config_file_cracker_config, connection_info)

        self.acquisition.load_config_from_str(acquisition_info)
        self.read_config_from_cracker()
        self.send({"loadConfigCompleted": True})

    def write_config_button_click(self, args: dict[str, typing.Any]):
        self.write_config_to_cracker()

    def read_config_button_click(self, args: dict[str, typing.Any]):
        self.read_config_from_cracker()

    def save_config_button_click(self, args: dict[str, typing.Any]):
        current_config_path = self._get_workspace_config_path()
        if current_config_path is None:
            return
        with open(current_config_path, "w") as f:
            self._logger.error(self._dump_config())
            f.write(self._dump_config())

    def _dump_config(self):
        def enum_converter(obj):
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(
            {
                "connection": self.uri,
                "cracker": self.get_cracker_panel_config().__dict__,
                "acquisition": self.get_acquisition_panel_config().__dict__,
            },
            indent=4,
            default=enum_converter,
        )

    def _load_current_path_config(self):
        """
        Load the workspace configuration if it exists.
        """
        config = self._get_workspace_config()

        if config is not None:
            connection_info = config.get("connection")
            config_info = config.get("cracker")
            acquisition_info = config.get("acquisition")

            self.cracker.load_config_from_str(config_info)
            self.cracker.set_uri(connection_info)
            self.acquisition.load_config_from_str(acquisition_info)
        else:
            self._logger.debug("Current config path is None or is no exist, current config will be ignored.")

    def _get_workspace_config(self):
        current_config_path = self._get_workspace_config_path()
        if current_config_path is None:
            return
        if current_config_path is not None and os.path.exists(current_config_path):
            with open(current_config_path) as f:
                try:
                    config = json.load(f)
                    return config
                except json.JSONDecodeError as e:
                    self._logger.error(f"Load workspace config file failed: {e.args}")
                    return None

    def _get_workspace_config_path(self):
        global_vars = sys.modules["__main__"].__dict__

        ipynb_path = None

        if "__vsc_ipynb_file__" in global_vars:
            ipynb_path = global_vars["__vsc_ipynb_file__"]
        elif "__session__" in global_vars:
            ipynb_path = global_vars["__session__"]

        if ipynb_path is not None:
            config_path = os.path.join(os.path.dirname(ipynb_path), ".config")
            if not os.path.exists(config_path):
                os.makedirs(config_path)
            elif os.path.isfile(config_path):
                self._logger.error(f"The config directory ({config_path}) already exists, and is not a directory.")
                return None
            return os.path.join(os.path.dirname(ipynb_path), ".config", os.path.basename(ipynb_path)[:-6] + ".json")

    @traitlets.observe("language")
    def on_language_change(self, change):
        user_config.set_option("language", change["new"])

    @staticmethod
    def builder():
        return CrackerG1PanelBuilder()

    @traitlets.observe("glitch_test_params")
    @observe_interceptor
    def glitch_test_params_changed(self, change):
        if isinstance(self.cracker, CrackerG1):
            self.acquisition.set_glitch_test_params(change.get("new"))
            # self.acquisition.glitch_run()


class CrackerG1PanelBuilder:
    def __init__(self):
        self._cracker: CrackerG1 | None = None
        self._acquisition_builder: GlitchAcquisitionBuilder | None = None
        self._acquisition_kwargs: dict = {}
        self._acquisition: Acquisition | None = None

    def with_cracker(self, cracker: CrackerG1) -> "CrackerG1PanelBuilder":
        self._cracker = cracker
        if self._acquisition_builder:
            self._acquisition_builder.cracker(cracker)
        return self

    def with_acquisition(
        self,
        init: typing.Callable[[], None],
        do: typing.Callable[[int], GlitchDoData],
        finish: typing.Callable[[], None],
        **kwargs,
    ) -> "CrackerG1PanelBuilder":
        """
        配置Acquisition(采集流程)参数

        :param init: 采集开始前的初始化函数，一般进行一些一次性配置，如电压配置、采样长度等
        :type init: typing.Callable[[], None]
        :param do: 采集函数，参数为采集次数，返回值为GlitchDoData对象
        :type do: typing.Callable[[int], GlitchDoData]
        :param finish: 采集结束后的清理函数，一般进行一些资源释放
        :type finish: typing.Callable[[], None]
        :param kwargs: 其他Acquisition参数
        :return: CrackerG1PanelBuilder对象
        :rtype: CrackerG1PanelBuilder
        """
        self._acquisition_builder = GlitchAcquisitionBuilder()
        self._acquisition_builder.init(init).do(do).finish(finish)
        if self._cracker:
            self._acquisition_builder.cracker(self._cracker)
        self._acquisition_kwargs = kwargs
        return self

    def build(self):
        self._acquisition = self._acquisition_builder.build(**self._acquisition_kwargs)
        return CrackerG1Panel(cracker=self._cracker, acquisition=self._acquisition)
