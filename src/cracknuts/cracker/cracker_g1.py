# Copyright 2024 CrackNuts. All rights reserved.
import re
import struct

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


class CommandG1(Command):
    GLITCH_VCC_ENABLE = 0x0310
    GLITCH_VCC_RESET = 0x0311
    GLITCH_VCC_FORCE = 0x0312
    GLITCH_VCC_CONFIG = 0x0313
    GLITCH_VCC_NORMAL = 0x0314

    GLITCH_GND_ENABLE = 0x0320
    GLITCH_GND_RESET = 0x0321
    GLITCH_GND_FORCE = 0x0322
    GLITCH_GND_CONFIG = 0x0323
    GLITCH_GND_NORMAL = 0x0324


class CrackerG1(CrackerS1):
    def glitch_vcc_enable(self):
        self._glitch_vcc_enable(True)

    def glitch_vcc_disable(self):
        self._glitch_vcc_enable(False)

    def _glitch_vcc_enable(self, enable: bool):
        payload = struct.pack(">?", enable)
        self._logger.debug(f"glitch_vcc_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_VCC_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def glitch_vcc_config(self, wait: int, g_level: int, g_cnt: int, g_delay: int, g_repeat: int):
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
        :param g_level: Glitch DAC电压值
        :type g_level: int
        :param g_cnt: Glitch持续时间（时钟个数）
        :type g_delay: int
        :param g_repeat: Glitch重复次数
        :type g_repeat: int
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None]
        """
        payload = struct.pack(">IIIII", wait, g_level, g_cnt, g_delay, g_repeat)
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
        return int(voltage / 5 / (2**10 - 1))

    def glitch_gnd_enable(self):
        self._glitch_gnd_enable(True)

    def glitch_gnd_disable(self):
        self._glitch_gnd_enable(False)

    def _glitch_gnd_enable(self, enable: bool):
        payload = struct.pack(">?", enable)
        self._logger.debug(f"glitch_gnd_enable payload: {payload.hex()}")
        status, res = self.send_with_command(CommandG1.GLITCH_GND_ENABLE, payload=payload)
        if status != protocol.STATUS_OK:
            return status, None
        else:
            return status, res

    def _glitch_gnd_config(self, wait: int, level: int, count: int, delay: int, repeat: int):
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

    def _get_config_bytes_format(self) -> tuple[dict[str, str], int, ConfigBasic]:
        bytes_format, bytes_length, config = super()._get_config_bytes_format()
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
        bytes_length = 50 + bytes_length
        config = ConfigG1()
        return bytes_format, bytes_length, config

    def get_default_config(self) -> ConfigS1:
        return ConfigG1()
