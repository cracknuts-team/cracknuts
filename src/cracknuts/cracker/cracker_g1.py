# Copyright 2024 CrackNuts. All rights reserved.

# Copyright 2024 CrackNuts. All rights reserved.
import os
import re
import struct
import typing

import pandas as pd
from scipy.interpolate import interp1d
import importlib.util
from cracknuts.cracker import protocol
from cracknuts.cracker.cracker_basic import ConfigBasic, connection_status_check
from cracknuts.cracker.cracker_s1 import ConfigS1, CrackerS1
from cracknuts.cracker.protocol import Command


class ConfigG1(ConfigS1):
    def __init__(self):
        super().__init__()
        self.glitch_vcc_arm = False
        self.glitch_vcc_normal = 3.3
        self.glitch_vcc_config_wait = 0
        self.glitch_vcc_config_level = self.glitch_vcc_normal
        self.glitch_vcc_config_count = 1
        self.glitch_vcc_config_delay = 0
        self.glitch_vcc_config_repeat = 1
        self.glitch_gnd_arm = False
        self.glitch_gnd_normal = 0
        self.glitch_gnd_config_wait = 0
        self.glitch_gnd_config_level = self.glitch_gnd_normal
        self.glitch_gnd_config_count = 1
        self.glitch_gnd_config_delay = 0
        self.glitch_gnd_config_repeat = 1
        self.glitch_clock_arm = False
        self.glitch_clock_len_normal = 0
        self.glitch_clock_wave_normal = 0
        self.glitch_clock_config_len_glitch = 0
        self.glitch_clock_config_wave_glitch = 0
        self.glitch_clock_config_count = 0
        self.glitch_clock_config_delay = 0
        self.glitch_clock_config_repeat = 0
        self.glitch_clock_normal = 0


class CommandG1(Command):
    GLITCH_VCC_ARM = 0x0310
    GLITCH_VCC_RESET = 0x0311
    GLITCH_VCC_FORCE = 0x0312
    GLITCH_VCC_CONFIG = 0x0313
    GLITCH_VCC_NORMAL = 0x0314

    GLITCH_GND_ARM = 0x0320
    GLITCH_GND_RESET = 0x0321
    GLITCH_GND_FORCE = 0x0322
    GLITCH_GND_CONFIG = 0x0323
    GLITCH_GND_NORMAL = 0x0324


def _build_interp_func(map_path) -> typing.Tuple[interp1d, interp1d]:
    df = pd.read_csv(map_path)
    x = df["code"].map(lambda v: int(v, 16)).values
    y = df["voltage"].values
    return interp1d(x, y, kind="linear", fill_value="extrapolate"), interp1d(y, x, kind="linear", fill_value="extrapolate")


_voltage_map_dir = os.path.join(os.path.dirname(importlib.util.find_spec("cracknuts").origin), "glitch", "voltage_map")
_vcc_interp_func_cv, _vcc_interp_func_vc = _build_interp_func(os.path.join(_voltage_map_dir, "vcc.csv"))
_gnd_interp_func_cv, _gnd_interp_func_vc = _build_interp_func(os.path.join(_voltage_map_dir, "gnd.csv"))
_clk_interp_func_cv, _clk_interp_func_vc = _build_interp_func(os.path.join(_voltage_map_dir, "clk.csv"))


class CrackerG1(CrackerS1):
    def __init__(
        self,
        address: tuple | str | None = None,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
    ):
        super().__init__(address, bin_server_path, bin_bitstream_path, operator_port)
        self._SYS_CLK_PERIOD_S = 6.25e-9

    @staticmethod
    def _get_dac_code_from_voltage(voltage: float, interp_func: interp1d) -> int:
        dac_code = int(round(interp_func(voltage * 1000).item()))
        return 0 if dac_code < 0 else 0x03FF if dac_code > 0x03FF else dac_code

    @staticmethod
    def _get_voltage_from_dac_code(dac_code: int, interp_func: interp1d) -> float:
        voltage = interp_func(dac_code).item() / 1000
        return voltage

    def glitch_vcc_arm(self):
        """
        设置glitch VCC 为armed状态。
        """
        self._glitch_vcc_arm(True)

    # def glitch_vcc_disable(self):
    #     self._glitch_vcc_enable(False)

    def _glitch_vcc_arm(self, enable: bool):
        payload = struct.pack(">?", enable)
        self._logger.debug(f"glitch_vcc_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_ARM, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_config(self, wait: int, level: int | float | str, length: int, delay: int, repeat: int):
        """
        配置glitch ::

            v_normal────┬───────────────────┐       ┌────────────┐       ┌───────
                        |       wait        | count |    delay   | count |
                        |                   |       |            |       |
                        |                   └───────┘            └───────┘ <--------- level voltage
                        |                       └────────────────────┘
                         Trigger                         repeat

        :param wait: glitch产生前等待时间（时钟个数）
        :type wait: int
        :param level: Glitch DAC电压值
        :type level: int
        :param length: Glitch持续时间, 单位 10ns
        :type delay: int
        :param repeat: Glitch重复次数
        :type repeat: int
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None]
        """
        level = self._get_dac_code_from_voltage(self._parse_voltage(level), _vcc_interp_func_vc)
        payload = struct.pack(">IIIII", wait, level, length, delay, repeat)
        self._logger.debug(f"glitch_vcc_config payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_CONFIG, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_reset(self):
        """
        重置glitch VCC配置。
        """
        self._logger.debug(f"glitch_vcc_reset payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_RESET, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_force(self):
        """
        强制触发glitch VCC。
        """
        self._logger.debug(f"glitch_vcc_force payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_FORCE, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def nut_voltage(self, voltage: float | str | int) -> tuple[int, None]:
        return self.glitch_vcc_normal(voltage)

    def glitch_vcc_normal(self, voltage: float | str | int) -> tuple[int, None]:
        """
        设置glitch VCC为正常电压值。
        """
        dac_code = self._get_dac_code_from_voltage(self._parse_voltage(voltage), _vcc_interp_func_vc)
        payload = struct.pack(">I", dac_code)
        self._logger.debug(f"glitch_vcc_normal payload: {payload}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_NORMAL, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def _parse_voltage(self, voltage: float | str | int):
        if isinstance(voltage, str):
            m = re.match(r"^(\d+(?:\.\d+)?)([mM]?[vV])?$", voltage)
            if not m:
                self._logger.error(
                    "Input format error: " "it should be a number or a string and end with a unit in V or mV."
                )
                return self.NON_PROTOCOL_ERROR, None
            voltage = float(m.group(1))
            if m.group(2):
                unit = m.group(2)
            else:
                unit = "v"
            if unit.lower() == "mv":
                voltage = voltage / 1000
        else:
            voltage = float(voltage)
        return voltage

    def glitch_gnd_arm(self):
        self._glitch_gnd_arm(True)

    # def glitch_gnd_disable(self):
    #     self._glitch_gnd_arm(False)

    def _glitch_gnd_arm(self, enable: bool):
        payload = struct.pack(">?", enable)
        self._logger.debug(f"glitch_gnd_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_ARM, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_gnd_config(self, wait: int, level: int, length: int, delay: int, repeat: int):
        level = self._get_dac_code_from_voltage(level, _gnd_interp_func_vc)
        payload = struct.pack(">IIIII", wait, level, length, delay, repeat)
        self._logger.debug(f"glitch_gnd_config payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_CONFIG, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_gnd_reset(self):
        self._logger.debug(f"glitch_vcc_reset payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_RESET, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_gnd_force(self):
        self._logger.debug(f"glitch_vcc_force payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_FORCE, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_gnd_normal(self, voltage: float | str | int) -> tuple[int, None]:
        dac_code = self._get_dac_code_from_voltage(self._parse_voltage(voltage), _gnd_interp_func_vc)
        payload = struct.pack(">I", dac_code)
        self._logger.debug(f"glitch_gnd_normal payload: {payload}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_NORMAL, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def _get_config_bytes_format(self) -> tuple[dict[str, str], ConfigBasic]:
        bytes_format, config = super()._get_config_bytes_format()
        bytes_format.update(
            {
                "glitch_vcc_arm": "?",
                "glitch_vcc_normal": "I",
                "glitch_vcc_config_wait": "I",
                "glitch_vcc_config_level": "I",
                "glitch_vcc_config_count": "I",
                "glitch_vcc_config_delay": "I",
                "glitch_vcc_config_repeat": "I",
                "glitch_gnd_arm": "?",
                "glitch_gnd_normal": "I",
                "glitch_gnd_config_wait": "I",
                "glitch_gnd_config_level": "I",
                "glitch_gnd_config_count": "I",
                "glitch_gnd_config_delay": "I",
                "glitch_gnd_config_repeat": "I",
            }
        )
        config = ConfigG1()
        return bytes_format, config

    def _parse_config_special_case(self, k, v):
        if k in ("glitch_vcc_normal", "glitch_vcc_config_level", "glitch_gnd_normal", "glitch_gnd_config_level"):
            v = round(self._get_voltage_from_dac_code(v, _vcc_interp_func_vc), 1)
        return v

    @connection_status_check
    def get_current_config(self) -> ConfigG1 | None:
        cur_cfg = typing.cast(ConfigG1, super().get_current_config())
        cur_cfg.nut_voltage = round(self._get_cracker_nut_vcc_voltage(), 1)
        cur_cfg.nut_clock = round(self._get_cracker_nut_clock())
        cur_cfg.nut_clock_enable = self._get_cracker_nut_clock_enabled()
        return cur_cfg

    def _get_cracker_nut_clock(self) -> float:
        """
        获取cracker当前nut时钟频率，单位kHz。
        :return: nut时钟频率，单位kHz
        :rtype: float
        """
        s, r = self.register_read(base_address=0x43c10000, offset=0x1D0)
        if s != protocol.STATUS_OK:
            return 0.0
        try:
            clock_len = struct.unpack('>I', r)[0]
            return 1 / (clock_len * self._SYS_CLK_PERIOD_S) / 1000
        except struct.error as e:
            self._logger.error(f"Unpack nut clock failed: {e}")
            return 0.0

    def _get_cracker_nut_vcc_voltage(self) -> float:
        """
        获取cracker当前nut电压，单位V。
        :return: nut电压，单位V
        :rtype: float
        """
        s, r = self.register_read(base_address=0x43c10000, offset=0x150)
        if s != protocol.STATUS_OK:
            return 0.0
        try:
            dac_code = struct.unpack('>I', r)[0]
            return self._get_voltage_from_dac_code(dac_code, _vcc_interp_func_cv)
        except struct.error as e:
            self._logger.error(f"Unpack nut voltage failed: {e}")
            return 0.0

    def _get_cracker_nut_clock_enabled(self) -> bool:
        """
        获取cracker当前nut时钟是否enabled。
        :return: nut时钟是否enabled
        :rtype: bool
        """
        s, r = self.register_read(base_address=0x43c10000, offset=0x1C4)
        if s != protocol.STATUS_OK:
            return False
        try:
            enabled = struct.unpack('>I', r)[0]
            return enabled == 0
        except struct.error as e:
            self._logger.error(f"Unpack nut clock enabled failed: {e}")
            return False

    def get_default_config(self) -> ConfigS1:
        return ConfigG1()

    def write_config_to_cracker(self, config: ConfigG1):
        super().write_config_to_cracker(config)
        self.glitch_vcc_normal(config.glitch_vcc_normal)
        self.glitch_vcc_config(
            config.glitch_gnd_config_wait,
            config.glitch_vcc_config_level,
            config.glitch_vcc_config_count,
            config.glitch_vcc_config_delay,
            config.glitch_vcc_config_repeat,
        )
        self.glitch_gnd_normal(config.glitch_gnd_normal)
        self.glitch_gnd_config(
            config.glitch_gnd_config_wait,
            config.glitch_gnd_config_level,
            config.glitch_gnd_config_count,
            config.glitch_gnd_config_delay,
            config.glitch_gnd_config_repeat,
        )

    # def set_glitch_test_params(self, param):
    #     self._glitch_test_params = param
    #
    # def get_glitch_test_params(self):
    #     return self._glitch_test_params

    def glitch_clock_normal(self, wave: list[float]) -> tuple[int, None|bytes]:
        status, res = self.register_write(base_address=0x43c10000, offset=0x1D0, data=len(wave))
        if status != protocol.STATUS_OK:
            return status, res
        for voltage in wave:
            status, res = self.register_write(base_address=0x43c10000, offset=0x1D4, data=self._get_dac_code_from_voltage(voltage, _clk_interp_func_vc))
            if status != protocol.STATUS_OK:
                return status, res
        return protocol.STATUS_OK, None

    def _glitch_clock_enable(self, enable: bool):
        return self.register_write(base_address=0x43c10000, offset=0x1C4, data=0 if enable else 1)

    def glitch_clock_enable(self):
        return self._glitch_clock_enable(True)

    def glitch_clock_disable(self):
        return self._glitch_clock_enable(False)

    def glitch_clock_config(self, wave: list[float], wait: int, delay: int, repeat: int) -> tuple[int, None|bytes]:
        status, res = self.register_write(base_address=0x43c10000, offset=0x1DC, data=len(wave))
        if status != protocol.STATUS_OK:
            return status, res
        for voltage in wave:
            status, res = self.register_write(base_address=0x43c10000, offset=0x1E0, data=self._get_dac_code_from_voltage(voltage, _clk_interp_func_vc))
            if status != protocol.STATUS_OK:
                return status, res
        self.register_write(base_address=0x43c10000, offset=0x1D8, data=wait)
        self.register_write(base_address=0x43c10000, offset=0x1E4, data=delay)
        self.register_write(base_address=0x43c10000, offset=0x1E8, data=repeat)

        return protocol.STATUS_OK, None

    def glitch_clock_arm(self):
        return self.register_write(base_address=0x43c10000, offset=0X1C8, data=1)

    def glitch_clock_reset(self):
        return self._glitch_clock_enable(False)

    def glitch_clock_force(self):
        return self.register_write(base_address=0x43c10000, offset=0x1CC, data=1)

    def _nut_set_clock_enable(self, enable: bool) -> tuple[int, None]:
        return self._glitch_clock_enable(enable)

    def nut_clock_freq(self, clock: int | str) -> tuple[int, None]:
        """
        Set nut clock.

        :param clock: The clock of the nut in kHz
        :type clock: int | str
        :return: The device response status
        :rtype: tuple[int, None]
        """
        wave_80m = [
            3.2,
            0
        ]
        wave_40m = [
            3.2, 3.2,
            0, 0
        ]
        wave_20m = [
            3.2, 3.2, 3.2, 3.2,
            0, 0, 0, 0,
        ]
        wave_16m = [
            3.2, 3.2, 3.2, 3.2, 3.2,
            0, 0, 0, 0, 0
        ]
        wave_10m = [
            3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
            0, 0, 0, 0, 0, 0, 0, 0,
        ]
        wave_8m = [
            3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        wave_4m = [
            3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        if isinstance(clock, str):
            m = re.match(r"^(\d+)[mM]$", clock)
            if m:
                clock = int(m.group(1)) * 1000
            else:
                self._logger.error("Input format error: it should be an integer or a string end with 'M'.")
                return protocol.STATUS_ERROR, None
        if clock == 80000:
            wave = wave_80m
        elif clock == 40000:
            wave = wave_40m
        elif clock == 20000:
            wave = wave_20m
        elif clock == 16000:
            wave = wave_16m
        elif clock == 10000:
            wave = wave_10m
        elif clock == 8000:
            wave = wave_8m
        elif clock == 4000:
            wave = wave_4m
        else:
            self._logger.error(f"Unknown clock type: {clock}, only support 80M, 40M, 20M, 16M, 10M, 8M, 4M")
            return protocol.STATUS_ERROR, None

        return self.glitch_clock_normal(wave)
