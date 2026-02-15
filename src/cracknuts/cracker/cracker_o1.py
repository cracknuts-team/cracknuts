from cracknuts.cracker import CrackerG1, protocol
from cracknuts.cracker.cracker_g1 import ConfigG1, _clk_interp_func_vc, wave_8m, wave_4m


class ConfigO1(ConfigG1):
    def __init__(self):
        super().__init__()
        self.glitch_clock_arm: bool = False
        self.glitch_clock_len_normal: int = len(wave_8m)
        self.glitch_clock_wave_normal: list[float] = wave_8m  # 默认时钟8mhz
        self.glitch_clock_config_len_glitch: int = len(wave_4m)
        self.glitch_clock_config_wave_glitch: list[float] = wave_4m  # 默认glitch示例时钟4mhz
        self.glitch_clock_config_wait: int = 1
        self.glitch_clock_config_delay: int = 1
        self.glitch_clock_config_repeat: int = 1
        self.glitch_clock_enable: bool = True


class CrackerO1(CrackerG1):
    def __init__(
        self,
        address: tuple | str | None = None,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None,
        operator_port: int = None,
    ):
        super().__init__(address, bin_server_path, bin_bitstream_path, operator_port)
        self._config: ConfigG1 = self._config

    def set_waveform(self, wave: list[float], wait: int, delay: int, repeat: int) -> tuple[int, None | bytes]:
        """
        param wave: 单组波形的电压值
        param wait: 波形触发后等待的周期数，单位为时钟周期
        param delay: 波形触发前的延迟周期数，单位为时钟周期
        param repeat: 波形重复的次数，单位为次数
        """
        ## 0x1800, 0x1C0
        status, res = self.register_write(base_address=0x43C10000, offset=0x181C, data=len(wave))
        if status != protocol.STATUS_OK:
            return status, res
        for voltage in wave:
            status, res = self.register_write(
                base_address=0x43C10000,
                offset=0x1820,
                data=self._get_dac_code_from_voltage(voltage, _clk_interp_func_vc),
            )
            if status != protocol.STATUS_OK:
                return status, res
        status, res = self.register_write(base_address=0x43C10000, offset=0x1818, data=wait)
        if status != protocol.STATUS_OK:
            return status, res
        self.register_write(base_address=0x43C10000, offset=0x1824, data=delay)
        if status != protocol.STATUS_OK:
            return status, res
        self.register_write(base_address=0x43C10000, offset=0x1828, data=repeat)
        if status != protocol.STATUS_OK:
            return status, res

        self._config.glitch_clock_config_wave_glitch = wave
        self._config.glitch_clock_config_len_glitch = len(wave)
        self._config.glitch_clock_config_wait = wait
        self._config.glitch_clock_config_repeat = repeat
        self._config.glitch_clock_config_delay = delay

        return protocol.STATUS_OK, None
