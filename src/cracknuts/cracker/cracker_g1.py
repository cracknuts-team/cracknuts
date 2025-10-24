# Copyright 2024 CrackNuts. All rights reserved.
import os
import re
import struct
import typing

import pandas as pd
from scipy.interpolate import interp1d
import importlib.util
from cracknuts.cracker import protocol
from cracknuts.cracker.cracker_basic import ConfigBasic
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


class CrackerG1(CrackerS1):
    def __init__(
        self,
        address: tuple | str | None = None,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
    ):
        super().__init__(address, bin_server_path, bin_bitstream_path, operator_port)
        # self._glitch_test_params = None
        df = pd.read_csv(
            os.path.join(os.path.dirname(importlib.util.find_spec("cracknuts").origin), "gnd_vnormal_voltage.csv")
        )
        codes = df["code"].map(lambda x: int(x, 16)).values
        voltages = df["voltage"].values
        self.interp_func_cv = interp1d(codes, voltages, kind="linear", fill_value="extrapolate")
        self.interp_func_vc = interp1d(voltages, codes, kind="linear", fill_value="extrapolate")

    def glitch_vcc_arm(self):
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

    def glitch_vcc_config(self, wait: int, level: int | float, count: int, delay: int, repeat: int):
        """
        配置glitch ::

            v_normal────┬───────────────────┐       ┌────────────┐       ┌───
                        |   wait_cnt        | g_cnt |  g_delay   | g_cnt |
                        |                   |       |            |       |
                        |           g_level └───────┘            └───────┘
                        |                       └────────────────────┘
                         Trigger                          g_repeat

        :param wait: glitch产生前等待时间（时钟个数）
        :type wait: int
        :param level: Glitch DAC电压值
        :type level: int
        :param count: Glitch持续时间（时钟个数）
        :type delay: int
        :param repeat: Glitch重复次数
        :type repeat: int
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None]
        """
        level = self._get_dac_code_from_voltage(level)
        payload = struct.pack(">IIIII", wait, level, count, delay, repeat)
        self._logger.debug(f"glitch_vcc_config payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_CONFIG, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_reset(self):
        self._logger.debug(f"glitch_vcc_reset payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_RESET, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_force(self):
        self._logger.debug(f"glitch_vcc_force payload: {None}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_FORCE, payload=None)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def nut_voltage(self, voltage: float | str | int) -> tuple[int, None]:
        return self.glitch_vcc_normal(voltage)

    def glitch_vcc_normal(self, voltage: float | str | int) -> tuple[int, None]:
        voltage = self._parse_voltage(voltage)
        dac_code = self._get_dac_code_from_voltage(voltage)
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

    def _get_dac_code_from_voltage(self, voltage: float) -> int:
        dac_code = int(round(self.interp_func_vc(voltage * 1000).item()))
        return 0 if dac_code < 0 else 0x03FF if dac_code > 0x03FF else dac_code

    def _get_voltage_from_dac_code(self, dac_code: int) -> float:
        voltage = self.interp_func_cv(dac_code).item() / 1000
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

    def glitch_gnd_config(self, wait: int, level: int, count: int, delay: int, repeat: int):
        level = self._get_dac_code_from_voltage(level)
        payload = struct.pack(">IIIII", wait, level, count, delay, repeat)
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
        voltage = self._parse_voltage(voltage)
        dac_code = self._get_dac_code_from_voltage(voltage)
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
            v = round(self._get_voltage_from_dac_code(v), 1)
        return v

    def get_current_config(self) -> ConfigG1 | None:
        cur_cfg = typing.cast(ConfigG1, super().get_current_config())
        cur_cfg.nut_voltage = cur_cfg.glitch_vcc_normal
        return cur_cfg

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
