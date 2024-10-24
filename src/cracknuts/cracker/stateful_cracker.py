# Copyright 2024 CrackNuts. All rights reserved.
from types import MethodType

from cracknuts.cracker.cracker import Cracker, Config


class StatefulCracker(Cracker):
    def __getattribute__(self, name):
        # todo 这里需要规范cracker的方法名称和配置的key名称，以便可以直接进行配置信息存储
        attr = super().__getattribute__(name)

        if isinstance(attr, MethodType):
            if name in object.__getattribute__(self, "__class__").__dict__:
                return attr
            else:
                cracker = super().__getattribute__("_cracker")
                return object.__getattribute__(cracker, name)
        return attr

    def __init__(self, cracker: Cracker):
        self._cracker = cracker
        self._config: Config = self._cracker.get_default_config()

    def get_current_config(self) -> Config:
        return self._config

    def sync_config_to_cracker(self):
        """
        Sync config to cracker.
        To prevent configuration inconsistencies between the host and the device,
        so all configuration information needs to be written to the device.
        User should call this function before get data from device.
        """
        # if self._config.nut_voltage is not None:
        #     self._cracker.nut_voltage(self._config.nut_voltage)
        # if self._config.nut_clock is not None:
        #     self._cracker.nut_clock(self._config.nut_clock)
        # if self._config.nut_enable is not None:
        #     self._cracker.nut_enable(self._config.nut_enable)
        # if self._config.osc_analog_channel_enable is not None:
        #     self._cracker.osc_set_analog_channel_enable(self._config.osc_analog_channel_enable)
        ...  # comment for test.
        # todo need complete...

    def osc_set_analog_channel_enable(self, enable: dict[int, bool]):
        self._config.osc_analog_channel_enable = enable
        return self._cracker.osc_set_analog_channel_enable(enable)

    def osc_set_sample_len(self, length: int):
        self._config.osc_sample_len = length
        return self._cracker.osc_set_sample_len(length)

    def nut_enable(self, enable: int):
        self._config.cracker_nut_enable = enable
        return self._cracker.nut_enable(enable)

    def nut_voltage(self, voltage: int):
        self._config.cracker_nut_voltage = voltage
        return self._cracker.nut_voltage(voltage)

    def nut_clock(self, clock: int):
        self._config.cracker_nut_clock = clock
        return self._cracker.nut_clock(clock)
