# Copyright 2024 CrackNuts. All rights reserved.

import os
import re
import struct
import math

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
    ):
        """
        Initialize the CrackNuts O1 device interface.

        :param address: Device address as ``(ip, port)``, URI string, or ``None``.
        :type address: tuple | str | None
        :param bin_server_path: Path to the server firmware file for updates; normally not specified.
        :type bin_server_path: str | None
        :param bin_bitstream_path: Path to the bitstream firmware file for updates; normally not specified.
        :type bin_bitstream_path: str | None
        """
        super().__init__(address, bin_server_path, bin_bitstream_path)
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
                    "GP28": 28,
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
        self._buffer_depth = 2048  # 任意波形缓冲区深度（采样点数量）
        self._wave_clk_div_max = 256

    def set_waveform_arbitrary(self, wave: list[float], wave_clk_div: int = 1) -> tuple[int, None | bytes]:
        """
        Set the waveform generator output waveform.

        :param wave: A sequence of voltage sample points for a single waveform period (unit: Volts).
            Each element represents the output voltage of one discrete sample point.
            The time interval per sample is 100 ns (corresponding to a 10 MHz sample rate).
            Samples are output in array order; one array represents one complete waveform period.
        :type wave: list[float]
        :param wave_clk_div: Waveform clock divider (integer, default 1).
            Actual output frequency = DAC sample rate / (len(wave) * wave_clk_div).
        :type wave_clk_div: int
        :return: Execution status code and device response data.
        :rtype: tuple[int, None | bytes]
        """

        if wave_clk_div < 1 or wave_clk_div > self._wave_clk_div_max:
            self._logger.error(f"wave_clk_div must be between 1 and {self._wave_clk_div_max}")
            return self.NON_PROTOCOL_ERROR, None

        status, res = self.register_write(
            base_address=0x43C10000, offset=0x182C, data=wave_clk_div - 1
        )  # 寄存器值为分频系数减1
        if status != protocol.STATUS_OK:
            return status, res

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
        Convert a frequency value to Hz.

        Supported formats: ``1e6``, ``1000000``, ``"1M"``, ``"1MHz"``, ``"500k"``,
        ``"500kHz"``, ``"2.5G"``, ``"10"`` (plain number defaults to Hz).

        :param frequency: Frequency value as a number or a string with optional unit suffix.
        :type frequency: int | float | str
        :return: Frequency in Hz.
        :rtype: float
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
            multiplier = 1
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
        Set standard waveform output.

        This function generates a single-period waveform dataset in software according to the specified
        parameters, writes it into the device arbitrary waveform buffer, and the DAC loops over it.

        Supported waveform types: ``"dc"`` (DC voltage), ``"sine"`` (sine wave),
        ``"square"`` (square wave), ``"triangle"`` (triangle wave), ``"sawtooth"`` (sawtooth wave).

        :param waveform: Waveform type name (case-insensitive).
        :type waveform: str
        :param vpp: Peak-to-peak voltage (Volts). For non-DC waveforms, amplitude = vpp / 2.
        :type vpp: float
        :param frequency: Output frequency (Hz). May be omitted for ``"dc"``; required for all others.
            Accepts a numeric value or a string with unit suffix (e.g. ``1e6``, ``"1MHz"``, ``"100kHz"``).
        :type frequency: float, str, or None
        :param offset: DC offset voltage (Volts). If ``None``, defaults to ``vpp / 2`` to keep the
            waveform non-negative.
        :type offset: float or None
        :param duty: Duty cycle or slope parameter between 0 and 1.
            For ``square``, this is the fraction of the period at high level.
            For ``sawtooth``, this is the fraction of the period occupied by the rising edge
            (near 1.0 means slow rise and fast fall; 0.5 gives a symmetric triangle;
            near 0.0 means fast rise and slow fall). Has no effect on ``sine`` or ``triangle``.
        :type duty: float
        :param phase: Initial phase in radians (2π rad = one full period).
        :type phase: float
        :return: Execution status code and device response data.
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
        if frequency > self._wave_fs:
            self._logger.error(
                "The frequency is too high to generate a valid waveform. " f"Maximum frequency is {self._wave_fs} Hz."
            )
            return self.NON_PROTOCOL_ERROR, None

        wave_clk_div = 1
        base_n_samples = max(1, int(self._wave_fs * 1.0 / frequency))
        if base_n_samples > self._buffer_depth:
            wave_clk_div = int(math.ceil(base_n_samples / self._buffer_depth))
            if wave_clk_div > self._wave_clk_div_max:
                min_freq = self._wave_fs / (self._buffer_depth * self._wave_clk_div_max)
                self._logger.error(
                    "The frequency is too low to generate a valid waveform. " f"Minimum frequency is {min_freq} Hz."
                )
                return self.NON_PROTOCOL_ERROR, None

        effective_fs = self._wave_fs / wave_clk_div
        n_samples = max(1, int(effective_fs * 1.0 / frequency))
        if n_samples > self._buffer_depth:
            self._logger.error(
                "The waveform is too long to fit in the buffer after applying wave_clk_div. "
                f"Length is {n_samples}, max is {self._buffer_depth}."
            )
            return self.NON_PROTOCOL_ERROR, None

        amplitude = vpp / 2

        if offset is None:
            offset = amplitude

        t = np.arange(n_samples) / effective_fs

        # Use sample-center time for phase-based waveforms to avoid low-sample aliasing.
        t_center = t + (0.5 / effective_fs)

        if waveform == "sine":
            wave = amplitude * np.sin(2 * np.pi * frequency * t + phase)

        elif waveform == "square":
            phase_t = (frequency * t_center + phase / (2 * np.pi)) % 1.0
            wave = np.where(phase_t < duty, amplitude, -amplitude)

        elif waveform == "triangle":
            phase_t = (frequency * t_center + phase / (2 * np.pi)) % 1.0
            wave = 4 * amplitude * np.abs(phase_t - 0.5) - amplitude

        elif waveform == "sawtooth":
            slope = np.clip(duty, 1e-6, 1 - 1e-6)

            phase_t = (frequency * t_center + phase / (2 * np.pi)) % 1.0

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

        return self.set_waveform_arbitrary(wave.tolist(), wave_clk_div=wave_clk_div)

    def set_waveform_sine(
        self,
        frequency: float | str,
        *,
        vpp: float = 1.0,
        phase: float = 0.0,
        offset: float | None = None,
    ):
        """
        Set sine wave output.

        :param frequency: Output frequency (Hz). Accepts a numeric value or a string with unit suffix,
            e.g. ``1e6``, ``"1m"``, ``"1MHz"``, ``"10kHz"``.
        :type frequency: float or str
        :param vpp: Peak-to-peak voltage (Volts). Default is 1.0.
        :type vpp: float
        :param phase: Initial phase in radians. Default is 0.0.
        :type phase: float
        :param offset: DC offset voltage (Volts). If ``None``, automatically set to ``vpp / 2``
            to avoid negative voltage.
        :type offset: float or None
        :return: Device response status and response data.
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
        Set square wave output.

        :param frequency: Output frequency (Hz).
        :type frequency: float
        :param duty: Duty cycle (0–1). 0.5 means a standard 50% square wave;
            0.2 means high level occupies 20% of the period. Default is 0.5.
        :type duty: float
        :param vpp: Peak-to-peak voltage (Volts). Default is 1.0.
        :type vpp: float
        :param phase: Initial phase in radians. Default is 0.0.
        :type phase: float
        :param offset: DC offset voltage (Volts).
        :type offset: float or None
        :return: Device response status and response data.
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
        Set triangle wave output.

        :param frequency: Output frequency (Hz).
        :type frequency: float
        :param vpp: Peak-to-peak voltage (Volts). Default is 1.0.
        :type vpp: float
        :param phase: Initial phase in radians. Default is 0.0.
        :type phase: float
        :param offset: DC offset voltage (Volts).
        :type offset: float or None
        :return: Device response status and response data.
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
        Set sawtooth wave output.

        :param frequency: Output frequency (Hz).
        :type frequency: float
        :param vpp: Peak-to-peak voltage (Volts). Default is 1.0.
        :type vpp: float
        :param slope: Fraction of the period occupied by the rising edge (0–1).
            1.0 = standard sawtooth (slow rise, fast fall); 0.5 = symmetric triangle;
            near 0 = fast rise, slow fall. Default is 1.0.
        :type slope: float
        :param phase: Initial phase in radians. Default is 0.0.
        :type phase: float
        :param offset: DC offset voltage (Volts).
        :type offset: float or None
        :return: Device response status and response data.
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
        Set DC voltage output.

        :param voltage: Output DC voltage (Volts). Must be within the device's allowed output range
            and must not be negative.
        :type voltage: float
        :return: Device response status and response data.
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
        Load waveform data from a file and set the output waveform.

        The file should contain a sequence of voltage sample points (unit: Volts),
        supporting comma-separated or newline-separated numeric formats.
        The maximum number of sample points is 2048.

        :param file_path: Path to a text file containing waveform data.
            Each numeric value in the file represents a voltage sample point (unit: V).
        :type file_path: str
        :return: Device response status and response data.
        :rtype: tuple[int, None | bytes]
        """

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

        if len(wave) > self._buffer_depth:
            self._logger.error(f"Waveform exceeds maximum length ({self._buffer_depth} samples).")
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
        Get the voltage at measurement point A0.

        :return: Device response status and measured voltage in Volts, or None on error.
        :rtype: tuple[int, float] or None
        """
        status, res = self.register_read(base_address=0x43C10000, offset=0x1E70)
        if status != protocol.STATUS_OK:
            return None
        return status, round(int.from_bytes(res, byteorder="big") / 16 / 4096 * 3.33, 2)

    def get_voltage_a1(self):
        """
        Get the voltage at measurement point A1.

        :return: Device response status and measured voltage in Volts, or None on error.
        :rtype: tuple[int, float] or None
        """
        status, res = self.register_read(base_address=0x43C10000, offset=0x1E40)
        if status != protocol.STATUS_OK:
            return None
        return status, round(int.from_bytes(res, byteorder="big") / 16 / 4096 * 3.33, 2)

    def set_pwm(self, freq, duty_cycle):
        """
        Set the PWM output on pin GP29.

        :param freq: PWM frequency in Hz.
        :type freq: float | int
        :param duty_cycle: PWM duty cycle as a fraction between 0 and 1.
        :type duty_cycle: float
        :return: Device response status and received data: (status, response).
        :rtype: tuple[int, None | bytes]
        """

        period = struct.pack(">I", round((freq * 2**32) / 100_000_000))
        duty = struct.pack(">I", round((1 - duty_cycle) * (2**32) - 1))

        status, res = self.register_write(base_address=0x43C10000, offset=0x1838, data=period)
        if status != protocol.STATUS_OK:
            return status, res
        status, res = self.register_write(base_address=0x43C10000, offset=0x183C, data=duty)
        if status != protocol.STATUS_OK:
            return status, res

        return protocol.STATUS_OK, None

    def get_switch_status_pl(self) -> tuple[int, None | tuple[int, int]]:
        """
        Get the PL switch status.

        :return: Status tuple ``(status, (sw1, sw2))``, where ``status`` is the protocol status code
            and ``sw1`` / ``sw2`` are the two PL switch state bits (0 = open, 1 = closed).
        :rtype: tuple[int, None | tuple[int, int]]
        """
        status, res = self.register_read(base_address=0x43C10000, offset=0x193C)
        if status != protocol.STATUS_OK:
            return status, res
        res = struct.unpack(">I", res)[0]
        sw1, sw2 = ((res >> i) & 1 for i in (0, 1))
        return status, (sw1, sw2)

    def get_switch_status_ps(self) -> tuple[int, None | tuple[int, int]]:
        """
        Get the PS switch status.

        :return: Status tuple ``(status, (sw1, sw2))``, where ``status`` is the protocol status code
            and ``sw1`` / ``sw2`` are the two PS switch state bits (0 = open, 1 = closed).
        :rtype: tuple[int, None | tuple[int, int]]
        """
        res = self._ssh_cracker.exec("gpioget -c 0 9 14", print_output=False)
        if res is not None and res["exit_code"] == 0:
            output = res["stdout"].strip()
            if output is not None and len(output) > 0:
                gpio_states = []
                for item in output.split():
                    _, state = item.split("=")
                    gpio_states.append(1 if state == "active" else 0)
                return protocol.STATUS_OK, tuple(gpio_states)
        return self.NON_PROTOCOL_ERROR, None

    def _load_image(self, image_path: str, fit: bool = True) -> np.ndarray | None:
        """
        Load an image and convert it to an RGB888 array.

        :param image_path: Path to the image file.
        :type image_path: str
        :param fit: Whether to resize the image to 64x64 pixels.
        :type fit: bool
        :return: Converted RGB888 array. Shape is ``(64, 64, 3)`` when ``fit=True``, or
            ``(H, W, 3)`` depending on the original image when ``fit=False``. Returns None on error.
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
        Set the LED display content.

        :param t: Content type: 0 for text, 1 for image.
        :type t: int
        :param x: X coordinate of the content in pixels.
        :type x: int
        :param y: Y coordinate of the content in pixels.
        :type y: int
        :param c: Content data: UTF-8 encoded string for text, or RGB888 byte array for images.
        :type c: bytes
        :param w: Width of the content in pixels. For text, this is the pixel width of the content;
            for images, this is the image width.
        :type w: int | None
        """
        if t == 0:
            payload = struct.pack(">Bii", t, x, y)
        else:
            payload = struct.pack(">BiiI", t, x, y, w)
        payload += c
        self.send_with_command(command=0x400, payload=payload)

    def set_led_text(self, text: str, x: int = 0, y: int = 0, auto_wrap: bool = True) -> None:
        """
        Set the LED display text. Only ASCII characters are supported. Each character is 5 pixels
        wide and 6 pixels tall with 1 pixel spacing. The screen resolution is 64x64 pixels with
        the origin at the top-left corner; x increases rightward and y increases downward.

        :param text: Text content to display.
        :type text: str
        :param x: X coordinate of the text in pixels.
        :type x: int
        :param y: Y coordinate of the text baseline in pixels. Note that the coordinate represents
            the baseline (bottom) of the text, so set y to 6 to display a complete first line.
        :type y: int
        :param auto_wrap: Whether to automatically wrap text when it exceeds the screen width.
        :type auto_wrap: bool
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
        Set the LED display image.

        :param image_path: Path to the image file; common formats such as PNG and JPEG are supported.
        :type image_path: str
        :param x: X coordinate of the image in pixels.
        :type x: int
        :param y: Y coordinate of the image in pixels.
        :type y: int
        :param fit: Whether to force-resize the image to 64x64 pixels.
            True: always resize to 64x64 regardless of original size.
            False: preserve the original image dimensions.
        :type fit: bool
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
        Read the level state of a digital IO pin. A high level requires more than 1.4 V.

        :param pin_id: Pin identifier. Supported pins: GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9.
        :type pin_id: str
        :return: Device response status and pin level: (status, level).
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
        Set the level state of a digital IO pin.

        :param pin_id: Pin identifier. Supported pins: GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9.
        :type pin_id: str
        :param value: Pin level state: 1 for high, 0 for low.
        :type value: int
        :return: Device response status and received data: (status, response).
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
        Set the operating mode of a digital IO pin.

        :param pin_id: Pin identifier. Supported pins: GP0-GP7, GP21-GP27, A, A2-A5, IO2-IO9.
        :type pin_id: str
        :param mode: Pin operating mode: 1 for input, 0 for output, or ``"INPUT"`` / ``"OUTPUT"``.
        :type mode: int | str
        :return: Device response status and received data: (status, response).
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
