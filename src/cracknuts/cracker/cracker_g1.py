# Copyright 2024 CrackNuts. All rights reserved.
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
        self.glitch_gnd_enable = False
        self.glitch_gnd_config_wait = 0
        self.glitch_gnd_config_level = 0
        self.glitch_gnd_config_count = 0
        self.glitch_gnd_config_delay = 0
        self.glitch_gnd_config_repeat = 0


class CommandG1(Command):
    GLITCH_VCC_ENABLE = 0x0310
    GLITCH_VCC_RESET = 0x0311
    GLITCH_VCC_FORCE = 0x0312
    GLITCH_VCC_CONFIG = 0x0313

    GLITCH_GND_ENABLE = 0x0320
    GLITCH_GND_RESET = 0x0321
    GLITCH_GND_FORCE = 0x0322
    GLITCH_GND_CONFIG = 0x0323


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

    def _get_config_bytes_format(self) -> tuple[dict[str, str], int, ConfigBasic]:
        self.glitch_vcc_enable = False
        self.glitch_vcc_config_wait = 0
        self.glitch_vcc_config_level = 0
        self.glitch_vcc_config_count = 0
        self.glitch_vcc_config_delay = 0
        self.glitch_vcc_config_repeat = 0
        self.glitch_gnd_enable = False
        self.glitch_gnd_config_wait = 0
        self.glitch_gnd_config_level = 0
        self.glitch_gnd_config_count = 0
        self.glitch_gnd_config_delay = 0
        self.glitch_gnd_config_repeat = 0

        bytes_format, bytes_length, config = super()._get_config_bytes_format()
        bytes_format.update(
            {
                "glitch_vcc_enable": "?",
                "glitch_vcc_config_wait": "I",
                "glitch_vcc_config_level": "I",
                "glitch_vcc_config_count": "I",
                "glitch_vcc_config_delay": "I",
                "glitch_vcc_config_repeat": "I",
                "glitch_gnd_enable": "?",
                "glitch_gnd_config_wait": "I",
                "glitch_gnd_config_level": "I",
                "glitch_gnd_config_count": "I",
                "glitch_gnd_config_delay": "I",
                "glitch_gnd_config_repeat": "I",
            }
        )
        bytes_length = 10
        config = ConfigG1()
        return bytes_format, bytes_length, config

    def get_default_config(self) -> ConfigS1:
        return ConfigG1()
