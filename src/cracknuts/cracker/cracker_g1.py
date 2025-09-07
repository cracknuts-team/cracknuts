# Copyright 2024 CrackNuts. All rights reserved.
import os
import re
import struct

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
        self.glitch_vcc_enable = False
        self.glitch_vcc_config_wait = 0
        self.glitch_vcc_config_level = 0
        self.glitch_vcc_config_count = 0
        self.glitch_vcc_config_delay = 0
        self.glitch_vcc_config_repeat = 0
        self.glitch_vcc_normal = 0
        self.glitch_gnd_enable = False
        self.glitch_gnd_config_wait = 0
        self.glitch_gnd_config_level = 0
        self.glitch_gnd_config_count = 0
        self.glitch_gnd_config_delay = 0
        self.glitch_gnd_config_repeat = 0
        self.glitch_gnd_normal = 0
        self.glitch_clock_enable = False
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

    @staticmethod
    def _get_dac_code_from_voltage(voltage: float) -> int:
        df = pd.read_csv(
            os.path.join(os.path.dirname(importlib.util.find_spec("cracknuts").origin), "gnd_vnormal_voltage.csv")
        )
        codes = df["code"].map(lambda x: int(x, 16)).values
        voltages = df["voltage"].values
        interp_func = interp1d(voltages, codes, kind="linear", fill_value="extrapolate")
        return int(round(interp_func(voltage * 1000).item()))

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
                "glitch_vcc_enable": "?",
                "glitch_vcc_normal": "I",
                "glitch_vcc_config_wait": "I",
                "glitch_vcc_config_level": "I",
                "glitch_vcc_config_count": "I",
                "glitch_vcc_config_delay": "I",
                "glitch_vcc_config_repeat": "I",
                "glitch_gnd_enable": "?",
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

    def get_default_config(self) -> ConfigS1:
        return ConfigG1()
