import os
import re
import struct

from PIL import Image

from cracknuts.cracker import protocol
from cracknuts.cracker.cracker_g1 import ConfigG1, CrackerG1, wave_8m, wave_4m, _build_interp_func
import numpy as np
import importlib.util

_wave_interp_func_cv, _wave_interp_func_vc = _build_interp_func(
    os.path.join(
        os.path.join(os.path.dirname(importlib.util.find_spec("cracknuts").origin), "cracker"),
        "o1_wave_voltage_map.csv",
    )
)


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
        """
        Cracker O1 设备接口类。
        """
        super().__init__(address, bin_server_path, bin_bitstream_path, operator_port)
        self._config: ConfigG1 = self._config
        self._gpio_map = {
            "r": {
                "mode": 0x194C,
                "output": 0x1950,
                "input": 0x1954,
                "index": {
                    "GP7": 7,
                    "GP0": 0,
                    "GP1": 1,
                    "GP2": 2,
                    "GP3": 3,
                    "GP4": 4,
                    "GP5": 5,
                    "GP6": 6,
                    "GP21": 21,
                    "GP22": 22,
                    "GP26": 26,
                    "GP23": 23,
                    "GP24": 24,
                    "GP27": 27,
                    "GP25": 25,
                },
            },
            "a": {
                "mode": 0x1940,
                "output": 0x1944,
                "input": 0x1948,
                "index": {
                    "A2": 19,
                    "A3": 18,
                    "A4": 17,
                    "A5": 16,
                    "IO2": 2,
                    "IO3": 3,
                    "IO4": 4,
                    "IO5": 5,
                    "IO6": 6,
                    "IO7": 7,
                    "IO8": 8,
                    "IO9": 9,
                    "A": 10,
                },
            },
        }
        self._wave_fs = 10_000_000  # DAC采样率
        self._buffer_depth = 160  # 160

    def set_waveform_arbitrary(self, wave: list[float]) -> tuple[int, None | bytes]:
        """
        设置波形发生器输出波形。

        :param wave: 单组波形的电压采样点序列（单位：伏特 V）。列表中每个元素表示一个离散采样点的输出电压值。
                     - 单个采样点时间间隔： 100 ns（对应 10 MHz 的采样率）
                     - 波形按照数组顺序依次输出
                     - 一个数组表示一个完整周期的波形
        :type wave: list[float]

        :return: 执行状态码与设备返回数据。
        :rtype: tuple[int, None | bytes]
        """
        status, res = self.register_write(base_address=0x43C10000, offset=0x1810, data=len(wave))
        if status != protocol.STATUS_OK:
            return status, res
        for voltage in wave:
            status, res = self.register_write(
                base_address=0x43C10000,
                offset=0x1814,
                data=self._get_dac_code_from_voltage(voltage, _wave_interp_func_vc),
            )
            if status != protocol.STATUS_OK:
                return status, res

        return protocol.STATUS_OK, None

    @staticmethod
    def _parse_frequency(frequency) -> float:
        """
        将 frequency 转为 Hz

        支持：
            1e6
            1000000
            "1M"
            "1MHz"
            "500k"
            "500kHz"
            "2.5G"
            "10"        -> 默认 MHz
        """

        if isinstance(frequency, int | float):
            return float(frequency)

        if not isinstance(frequency, str):
            raise TypeError("frequency must be float | int | str")

        s = frequency.strip().lower()

        units = {
            "hz": 1,
            "k": 1e3,
            "khz": 1e3,
            "m": 1e6,
            "mhz": 1e6,
            "g": 1e9,
            "ghz": 1e9,
        }

        m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([a-z]*)", s)
        if not m:
            raise ValueError(f"Invalid frequency format: {frequency}")

        value = float(m.group(1))
        unit = m.group(2)

        if unit == "":
            multiplier = 1e6
        else:
            if unit not in units:
                raise ValueError(f"Unknown frequency unit: {unit}")
            multiplier = units[unit]

        return value * multiplier

    def set_waveform_standard(
        self,
        waveform: str,
        vpp,
        *,
        frequency: str | float | None = None,
        offset: float | None = None,
        duty: float = 0.5,
        phase: float = 0.0,
    ) -> tuple[int, None | bytes]:
        """
        设置标准波形输出。

        本函数根据指定参数在软件中生成 **单周期波形数据**，并写入设备任意波形缓冲区，由 DAC 循环播放该波形。

        支持波形类型：

        - ``"dc"``       ：直流电压
        - ``"sine"``     ：正弦波
        - ``"square"``   ：方波
        - ``"triangle"`` ：三角波
        - ``"sawtooth"`` ：锯齿波（可调坡度）

        :param waveform: 波形类型名称（大小写不敏感）。
        :type waveform: str
        :param vpp: 峰峰值电压（Volt）。对于非 DC 波形，振幅 `amplitude = vpp / 2`。
        :type vpp: float
        :param frequency: 输出频率（Hz）。对 ``"dc"`` 可省略，其他波形必须指定。
                          支持数值或带单位字符串（例如 `1e6`、`"1MHz"`、`"100kHz"`）。
        :type frequency: float, str, or None, optional
        :param offset: 直流偏置电压（Volt）。若为 `None`，默认 `offset = vpp / 2`，保证波形非负。
        :type offset: float or None, optional

        :param duty: 波形占空比 / 坡度参数（0~1）。
                     - ``square``：高电平占周期比例
                     - ``sawtooth``：上升段占周期比例
                       - 接近 1 → 慢上升 + 快下降（标准锯齿波）
                       - 0.5 → 对称三角波
                       - 接近 0 → 快速上升 + 慢下降
                     - 对 ``sine`` 与 ``triangle`` 无作用
        :type duty: float, optional
        :default duty: 0.5
        :param phase: 初始相位（弧度 rad）。数学定义：`2π rad = 1 个周期`
        :type phase: float, optional
        :default phase: 0.0
        :return: 执行状态码与设备返回数据。
        :rtype: tuple[int, None | bytes]
        """

        waveform = waveform.lower()

        if waveform == "dc":
            wave = np.full(1, vpp, dtype=float)
            return self.set_waveform_arbitrary(wave.tolist())

        if frequency is None:
            self._logger.error("frequency must be specified for non-DC waveform")
            return self.NON_PROTOCOL_ERROR, None
        frequency = self._parse_frequency(frequency)
        if frequency < self._wave_fs / self._buffer_depth:
            self._logger.error(
                "The frequency is too low to generate a valid waveform. "
                f"Minimum frequency is {self._wave_fs / self._buffer_depth} Hz."
            )
            return self.NON_PROTOCOL_ERROR, None
        elif frequency > self._wave_fs:
            self._logger.error(
                "The frequency is too high to generate a valid waveform. " f"Maximum frequency is {self._wave_fs} Hz."
            )
            return self.NON_PROTOCOL_ERROR, None

        amplitude = vpp / 2

        if offset is None:
            offset = amplitude

        n_samples = max(1, int(self._wave_fs * 1.0 / frequency))
        t = np.arange(n_samples) / self._wave_fs

        if waveform == "sine":
            wave = amplitude * np.sin(2 * np.pi * frequency * t + phase)

        elif waveform == "square":
            phase_t = (frequency * t + phase / (2 * np.pi)) % 1.0
            wave = np.where(phase_t < duty, amplitude, -amplitude)

        elif waveform == "triangle":
            phase_t = (frequency * t + phase / (2 * np.pi)) % 1.0
            wave = 4 * amplitude * np.abs(phase_t - 0.5) - amplitude

        elif waveform == "sawtooth":
            slope = np.clip(duty, 1e-6, 1 - 1e-6)

            phase_t = (frequency * t + phase / (2 * np.pi)) % 1.0

            wave = np.where(
                phase_t < slope,
                -amplitude + (2 * amplitude / slope) * phase_t,
                amplitude - (2 * amplitude / (1 - slope)) * (phase_t - slope),
            )

        else:
            raise ValueError(f"Unsupported waveform: {waveform}")

        wave = wave + offset

        v_min = float(np.min(wave))
        if v_min < 0:
            raise ValueError("Generated waveform contains negative voltage. " "Increase offset or reduce amplitude.")

        return self.set_waveform_arbitrary(wave.tolist())

    def set_waveform_sine(
        self,
        frequency: float | str,
        *,
        vpp: float = 1.0,
        phase: float = 0.0,
        offset: float | None = None,
    ):
        """
        设置正弦波输出。

        :param frequency: 输出频率（Hz）。支持数值或带单位的字符串形式，例如 `1e6`、`1m`、`"1MHz"`、`"10kHz"`。
        :type frequency: float or str
        :param vpp: 峰峰值电压（Volt）。
        :type vpp: float, optional
        :default vpp: 1.0
        :param phase: 初始相位（弧度 rad）。
        :type phase: float, optional
        :default phase: 0.0
        :param offset: 直流偏置电压（Volt）。若为 `None`，默认自动设置为 `vpp / 2` 以避免负电压。
        :type offset: float or None, optional
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """
        return self.set_waveform_standard(
            "sine",
            vpp=vpp,
            frequency=frequency,
            phase=phase,
            offset=offset,
        )

    def set_waveform_square(
        self,
        frequency: float,
        *,
        duty: float = 0.5,
        vpp: float = 1.0,
        phase: float = 0.0,
        offset: float | None = None,
    ):
        """
        设置方波输出。

        :param frequency: 输出频率（Hz）。
        :type frequency: float
        :param duty: 占空比（0~1）。
                     - 0.5 表示标准 50% 方波
                     - 0.2 表示高电平占 20% 周期
        :type duty: float, optional
        :default duty: 0.5
        :param vpp: 峰峰值电压（Volt）。
        :type vpp: float, optional
        :default vpp: 1.0
        :param phase: 初始相位（弧度 rad）。
        :type phase: float, optional
        :default phase: 0.0
        :param offset: 直流偏置电压（Volt）。
        :type offset: float or None, optional
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """
        return self.set_waveform_standard(
            "square",
            frequency=frequency,
            vpp=vpp,
            duty=duty,
            phase=phase,
            offset=offset,
        )

    def set_waveform_triangle(
        self,
        frequency: float,
        *,
        vpp: float = 1.0,
        phase: float = 0.0,
        offset: float | None = None,
    ):
        """
        设置三角波输出。

        :param frequency: 输出频率（Hz）。
        :type frequency: float
        :param vpp: 峰峰值电压（Volt）。
        :type vpp: float, optional
        :default vpp: 1.0
        :param phase: 初始相位（弧度 rad）。
        :type phase: float, optional
        :default phase: 0.0
        :param offset: 直流偏置电压（Volt）。
        :type offset: float or None, optional
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """
        return self.set_waveform_standard(
            "triangle",
            frequency=frequency,
            vpp=vpp,
            phase=phase,
            offset=offset,
        )

    def set_waveform_sawtooth(
        self,
        frequency: float,
        *,
        vpp: float = 1.0,
        slope: float = 1.0,
        phase: float = 0.0,
        offset: float | None = None,
    ):
        """
        设置锯齿波输出。

        :param frequency: 输出频率（Hz）。
        :type frequency: float
        :param vpp: 峰峰值电压（Volt）。
        :type vpp: float, optional
        :default vpp: 1.0
        :param slope: 上升段占整个周期的比例（0~1）。
                      - 1.0 → 标准锯齿波（慢上升，快下降）
                      - 0.5 → 对称三角波
                      - 接近 0 → 快速上升，慢下降
        :type slope: float, optional
        :default slope: 1.0
        :param phase: 初始相位（弧度 rad）。
        :type phase: float, optional
        :default phase: 0.0
        :param offset: 直流偏置电压（Volt）。
        :type offset: float or None, optional
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """
        return self.set_waveform_standard(
            "sawtooth",
            frequency=frequency,
            vpp=vpp,
            duty=slope,
            phase=phase,
            offset=offset,
        )

    def set_waveform_dc(self, voltage: float):
        """
        设置直流电压输出。

        :param voltage: 输出直流电压（Volt）。电压值必须在设备允许的输出范围内，且不得为负值。
        :type voltage: float
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """
        return self.set_waveform_standard(
            "dc",
            frequency=1.0,
            vpp=voltage,
            offset=voltage,
        )

    def set_waveform_from_file(self, file_path: str) -> tuple[int, None | bytes]:
        """
        从文件加载波形数据并设置输出波形。

        文件内容应为电压采样点序列（单位：伏特 V），
        支持逗号分隔或逐行排列的数值格式。
        采样点数量最大不得超过 160 个。

        :param file_path: 包含波形数据的文本文件路径。
                          文件中每个数值表示一个电压采样点（单位 V）。
        :type file_path: str
        :return: 设备返回状态与响应数据。
        :rtype: tuple[int, None | bytes]
        """

        import os
        import numpy as np

        # ---------- 文件检查 ----------
        if not os.path.exists(file_path):
            self._logger.error(f"Waveform file not found: {file_path}")
            return self.NON_PROTOCOL_ERROR, None

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self._logger.error(f"Failed to read waveform file: {e}")
            return self.NON_PROTOCOL_ERROR, None

        # ---------- 解析数据 ----------
        # 支持：
        # 1,2,3
        # 1 2 3
        # 1\n2\n3
        tokens = content.replace(",", " ").split()

        if not tokens:
            self._logger.error("Waveform file is empty.")
            return self.NON_PROTOCOL_ERROR, None

        try:
            wave = np.array([float(v) for v in tokens], dtype=float)
        except ValueError:
            self._logger.error("Waveform file contains non-numeric values.")
            return self.NON_PROTOCOL_ERROR, None

        max_points = 160
        if len(wave) > max_points:
            self._logger.error(f"Waveform exceeds maximum length ({max_points} samples).")
            return self.NON_PROTOCOL_ERROR, None

        if not np.all(np.isfinite(wave)):
            self._logger.error("Waveform contains NaN or Inf.")
            return self.NON_PROTOCOL_ERROR, None

        v_min = float(np.min(wave))
        if v_min < 0:
            self._logger.error("Waveform contains negative voltage. " "All samples must be >= 0 V.")
            return self.NON_PROTOCOL_ERROR, None

        return self.set_waveform_arbitrary(wave.tolist())

    def get_voltage_a0(self):
        """
        获取测量点a0电压
        """
        status, res = self.register_read(base_address=0x43C10000, offset=0x1E70)
        if status != protocol.STATUS_OK:
            return None
        return status, round(int.from_bytes(res, byteorder="big") / 16 / 4096 * 3.33, 2)

    def get_voltage_a1(self):
        """
        获取测量点a1电压
        """
        status, res = self.register_read(base_address=0x43C10000, offset=0x1E40)
        if status != protocol.STATUS_OK:
            return None
        return status, round(int.from_bytes(res, byteorder="big") / 16 / 4096 * 3.33, 2)

    def set_pwm(self, pin, freq, duty_cycle):
        """
        设置PWM输出
        :param pin: PWM输出引脚，GP28或GP29
        :param freq: PWM频率，单位Hz
        :param duty_cycle: PWM占空比，0-1之间的小数
        """

        period = struct.pack(">I", round((freq * 2**32) / 100_000_000))
        duty = struct.pack(">I", round((1 - duty_cycle) * (2**32) - 1))

        pin = pin.upper()

        if pin == "GP29":
            status, res = self.register_write(base_address=0x43C10000, offset=0x1838, data=period)
            if status != protocol.STATUS_OK:
                return status, res
            status, res = self.register_write(base_address=0x43C10000, offset=0x183C, data=duty)
            if status != protocol.STATUS_OK:
                return status, res
        elif pin == "GP28":
            status, res = self.register_write(base_address=0x43C10000, offset=0x1830, data=period)
            if status != protocol.STATUS_OK:
                return status, res
            status, res = self.register_write(base_address=0x43C10000, offset=0x1834, data=duty)
            if status != protocol.STATUS_OK:
                return status, res
        else:
            self._logger.error(f"pin {pin} not supported")
            return self.NON_PROTOCOL_ERROR, None

        return protocol.STATUS_OK, None

    def set_pwm_gp28(self, freq, duty_cycle):
        """
        设置GP28的PWM输出
        :param freq: PWM频率，单位Hz
        :param duty_cycle: PWM占空比，0-1之间的小数
        """
        return self.set_pwm("GP28", freq, duty_cycle)

    def set_pwm_gp29(self, freq, duty_cycle):
        """
        设置GP29的PWM输出
        :param freq: PWM频率，单位Hz
        :param duty_cycle: PWM占空比，0-1之间的小数
        """
        return self.set_pwm("GP29", freq, duty_cycle)

    def get_switch_status(self, switch_id: str) -> tuple[int, None | tuple[int, int]]:
        """
        获取开关状态

        :param switch_id: 开关ID，'pl'或'ps'
        :type switch_id: str
        :return: (status, (sw1, sw2))，其中status为协议状态码，
                 sw1和sw2分别为开关的两个状态位, 0表示开关关闭，1表示开关打开
        """
        switch_id = switch_id.lower()
        if switch_id == "pl":
            offset = 0x193C
        elif switch_id == "ps":
            offset = 0x193C
        else:
            self._logger.error(f"switch_id {switch_id} not supported")
            return self.NON_PROTOCOL_ERROR, None
        status, res = self.register_read(base_address=0x43C10000, offset=offset)
        if status != protocol.STATUS_OK:
            return status, res
        res = struct.unpack(">I", res)[0]
        sw1, sw2 = ((res >> i) & 1 for i in (0, 1))
        return status, (sw1, sw2)

    def get_switch_status_pl(self) -> tuple[int, None | tuple[int, int]]:
        """
        获取PL开关状态
        :return: (status, (sw1, sw2))，其中status为协议状态码，
                 sw1和sw2分别为PL开关的两个状态位, 0表示开关关闭，1表示开关打开
        """
        return self.get_switch_status("pl")

    def get_switch_status_ps(self) -> tuple[int, None | tuple[int, int]]:
        """
        获取PS开关状态
        :return: (status, (sw1, sw2))，其中status为协议状态码，
                 sw1和sw2分别为PS开关的两个状态位, 0表示开关关闭，1表示开关打开
        """
        return self.get_switch_status("ps")

    def _load_image(self, image_path: str, fit: bool = True) -> np.ndarray | None:
        """
        读取图片并转换为 RGB888 数组。

        :param image_path: 图片路径。
        :type image_path: str

        :return: 转换后的 RGB888 数组。
                 - 若 `should_resize=True`：形状为 (64, 64, 3)
                 - 若 `should_resize=False`：形状为 (H, W, 3)，取决于原图
                 - 出错时返回 None
        :rtype: np.ndarray or None
        """
        target_size = 64

        try:
            with Image.open(image_path) as img:
                # 1. 强制转换为 RGB 模式 (处理 RGBA, 灰度等)
                rgb_img = img.convert("RGB")
                width, height = rgb_img.size

                processing_img = rgb_img

                if fit:
                    # 无论原图大小，统一缩放至 64x64
                    # LANCZOS 算法在缩小和放大时都能提供较好的质量
                    processing_img = rgb_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                    # print(f"Image resized from {width}x{height} to {target_size}x{target_size}")
                else:
                    # 保持原图
                    # print(f"Resize disabled, kept original size {width}x{height}.")
                    pass

                # 2. 转换为 NumPy 数组
                rgb_array = np.array(processing_img, dtype=np.uint8)

                # 3. 验证形状 (仅在开启缩放时验证)
                if fit:
                    if rgb_array.shape != (64, 64, 3):
                        self._logger.warning(f"Expected shape (64, 64, 3), got {rgb_array.shape}")

                return rgb_array

        except FileNotFoundError:
            self._logger.error(f"Image {image_path} not exist")
            return None
        except Exception as e:
            self._logger.error(f"Load image failed: {e}")
            return None

    def set_led_content(self, t: int, x: int, y: int, c: bytes, w: int = None) -> None:
        """
        设置LED显示内容

        :param t: 显示内容类型，0表示文本，1表示图片
        :param x: 显示内容的x坐标，单位为像素
        :param y: 显示内容的y坐标，单位为像素
        :param c: 显示内容，文本类型为UTF-8编码的字符串，图片类型为RGB888格式的字节数组
        :param w: 显示内容的宽度，单位为像素，文本类型为内容的像素宽度，图片类型为图片的宽度
        """
        if t == 0:
            payload = struct.pack(">Bii", t, x, y)
        else:
            payload = struct.pack(">BiiI", t, x, y, w)
        payload += c
        self.send_with_command(command=0x400, payload=payload)

    def set_led_text(self, text: str, x: int = 0, y: int = 0, auto_wrap: bool = True) -> None:
        """
        设置LED显示文本，仅支持英文字符显示。字符宽度为5像素，高度为6像素，字符间距为1像素。
        屏幕分辨率为64x64像素，坐标原点在屏幕左上角，x坐标向右增加，y坐标向下增加。

        :param text: 显示文本内容
        :param x: 显示文本的x坐标，单位为像素
        :param y: 显示文本的y坐标，单位为像素。
                  注意，坐标表示文本基线的位置，即文本的底部位置。所以如果要显示完整的一行文字，则要设置y为6（字符高度为6）
        """
        if auto_wrap:
            max_chars_per_line = (64 - x) // 6  # 每行最多显示的字符数（5像素字符宽度 + 1像素间距）
            lines = []
            current_line = ""
            for char in text:
                if len(current_line) < max_chars_per_line:
                    current_line += char
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            text = "\n".join(lines)
        self.set_led_content(0, x, y, text.encode("utf-8"))

    def set_led_image(self, image_path: str, x: int = 0, y: int = 0, fit: bool = True) -> None:
        """
        设置LED显示图片

        :param image_path: 图片文件路径，支持常见格式如PNG、JPEG等
        :param x: 显示图片的x坐标，单位为像素
        :param y: 显示图片的y坐标，单位为像素
        :param fit: 是否强制缩放图片至64x64像素
             - True: 无论原图大小，统一缩放至64x64。
             - False: 保持原图尺寸，不进行缩放。
        """
        img_array = self._load_image(image_path, fit)
        if img_array is not None:
            h, w, _ = img_array.shape
            self.set_led_content(1, x, y, img_array.tobytes(), w)

    def _get_gpio_offset_and_index(self, pin_id: str):
        pin_id = pin_id.upper()
        if pin_id.startswith("GP"):
            pin_index = self._gpio_map["r"]["index"].get(pin_id, None)
            output_offset = self._gpio_map["r"]["output"]
            input_offset = self._gpio_map["r"]["input"]
            mode = self._gpio_map["r"]["mode"]
        elif pin_id.startswith("A") or pin_id.startswith("IO"):
            pin_index = self._gpio_map["a"]["index"].get(pin_id, None)
            output_offset = self._gpio_map["a"]["output"]
            input_offset = self._gpio_map["a"]["input"]
            mode = self._gpio_map["a"]["mode"]
        else:
            self._logger.error(f"pin_id {pin_id} not supported")
            return self.NON_PROTOCOL_ERROR, None

        return pin_index, output_offset, input_offset, mode

    def digital_read(self, pin_id: str):
        """
        读取数字IO引脚电平状态，高电平需要大于 1.4v

        :param pin_id: 引脚ID, 支持 GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9
        :type pin_id: str
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None | int]
        """
        pin_index, _, offset, _ = self._get_gpio_offset_and_index(pin_id)
        if pin_index is None or offset is None:
            self._logger.error(f"pin_id {pin_id} not supported")
            return self.NON_PROTOCOL_ERROR, None

        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=offset)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get GPIO data failed, status: {s}")
            return s, r
        else:
            return s, self._get_bit_stream_lsb(r, pin_index)

    def digital_write(self, pin_id: str, value: int):
        """
        设置数字IO引脚电平状态

        :param pin_id: 引脚ID, 支持 GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9
        :type pin_id: str
        :param value: 引脚电平状态，1：高电平，0：
        :type value: int
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None]
        """
        pin_index, offset, _, _ = self._get_gpio_offset_and_index(pin_id)
        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=offset)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get old GPIO data failed, status: {s}")
            return s, r
        else:
            gpio_data = int.from_bytes(r, byteorder="big")
            if value:
                gpio_data |= 1 << pin_index
            else:
                gpio_data &= ~(1 << pin_index)
            gpio_data_bytes = gpio_data.to_bytes(len(r), byteorder="big")
            return self.register_write(base_address=self._BASE_ADDRESS, offset=offset, data=gpio_data_bytes)

    def digital_pin_mode(self, pin_id: str, mode: int | str):
        """
        设置数字IO引脚工作模式

        :param pin_id: 引脚ID, 支持 GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9
        :type pin_id: str
        :param mode: 引脚工作模式，1：输入模式，0：输出模式，或者 "INPUT"、"OUTPUT"
        :type mode: int | str
        :return: Cracker设备响应状态和接收到的数据：(status, response)。
        :rtype: tuple[int, bytes | None]
        """
        if isinstance(mode, str):
            if mode.upper() == "INPUT":
                mode = 1
            elif mode.upper() == "OUTPUT":
                mode = 0
            else:
                raise ValueError("Invalid mode string, must be 'INPUT' or 'OUTPUT'")
        pin_index, _, _, offset = self._get_gpio_offset_and_index(pin_id)
        s, r = self.register_read(base_address=self._BASE_ADDRESS, offset=offset)
        if s != protocol.STATUS_OK:
            self._logger.error(f"Get old GPIO mode failed, status: {s}")
            return s, r
        else:
            gpio_dir = int.from_bytes(r, byteorder="big")
            if mode:
                gpio_dir |= 1 << pin_index
            else:
                gpio_dir &= ~(1 << pin_index)
            gpio_dir_bytes = gpio_dir.to_bytes(len(r), byteorder="big")
            return self.register_write(base_address=self._BASE_ADDRESS, offset=offset, data=gpio_dir_bytes)
