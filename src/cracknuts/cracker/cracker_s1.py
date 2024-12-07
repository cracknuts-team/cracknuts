# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.cracker.cracker import CommonConfig, CommonCracker


class CrackerS1Config(CommonConfig):
    def __init__(self):
        super().__init__()
        self.nut_enable = False
        self.nut_voltage = 3500
        self.nut_clock = 100

        self.osc_analog_channel_enable = {1: False, 2: True}
        self.osc_analog_gain = {1: 50, 2: 50}
        self.osc_sample_len = 1024
        self.osc_sample_delay = 0
        self.osc_sample_clock = 62500
        self.osc_sample_phase = 0
        self.osc_analog_trigger_source = 0
        self.osc_trigger_mode = 0
        self.osc_analog_trigger_edge = 0
        self.osc_analog_trigger_edge_level = 1


class CrackerS1(CommonCracker[CrackerS1Config]):
    def get_default_config(self) -> CrackerS1Config:
        return CrackerS1Config()
