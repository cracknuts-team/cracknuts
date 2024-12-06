# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.cracker.cracker import CommonConfig, CommonCracker


class CrackerS1Config(CommonConfig):
    def __init__(self):
        super().__init__()


class CrackerS1(CommonCracker[CrackerS1Config]):
    def get_default_config(self) -> CrackerS1Config:
        default_config = CrackerS1Config()
        default_config.nut_voltage = 3500
        default_config.osc_analog_channel_enable = {1: False, 2: True}
        default_config.osc_sample_len = 1024
        default_config.osc_analog_gain = {1: 50, 2: 50}
        return default_config
