# Copyright 2024 CrackNuts. All rights reserved.

import threading
import time
import typing

import numpy as np

from cracknuts.cracker.cracker_basic import CrackerBasic
from cracknuts import logger
from cracknuts.cracker import protocol


class ScopeAcquisition:
    def __init__(self, cracker: CrackerBasic, interval: float = 0.05, repeat_interval: float = 0.1):
        self._logger = logger.get_logger(self)
        self._status: int = 0  # 0 stop, 1 normal, 2 single, 3 repeat
        self._cracker: CrackerBasic = cracker
        self._offset: int = 0
        self._last_waves = {}
        self._run_thread_pause_event: threading.Event = threading.Event()
        self._interval: float = interval
        self._trigger_judge_wait_time: float = 0.01
        self._repeat_interval: float = repeat_interval
        self._status_change_listener: list[typing.Callable[[int], None]] = []

    def on_status_changed(self, callback: typing.Callable[[int], None]) -> None:
        self._status_change_listener.append(callback)

    def _status_changed(self):
        for listener in self._status_change_listener:
            listener(self._status)

    def set_offset(self, offset: int):
        self._offset = offset

    def is_running(self) -> bool:
        return self._status != 0

    def run(self, model: int = 1) -> None:
        if model == 0:
            self.stop()
        else:
            if self._status == 0:
                # When starting from the stopped state, clear the waveform data left from the previous acquisition.
                self._last_waves = {}
                self._status = model
                threading.Thread(target=self._acquisition, kwargs={"model": model}).start()
                self._status_changed()
            else:
                self._status = model

    def stop(self):
        if not self._run_thread_pause_event.is_set():
            self._run_thread_pause_event.set()
        self._status = 0
        self._status_changed()

    def resume(self):
        if self._status < 0:
            self._run_thread_pause_event.clear()
            self._status = -1 * abs(self._status)
            self._status_changed()

    def pause(self):
        self._status = abs(self._status)
        self._status_changed()

    def start_normal(self):
        self.run(1)

    def start_single(self):
        self.run(2)

    def start_repeat(self):
        self.run(3)

    def _acquisition(self, model: int):
        while self._status != 0:
            if self._status < 0:
                if self._status == -2:
                    # Pause is not supported in single model. it will exit.
                    self._run_thread_pause_event.set()
                    self.stop()
                else:
                    self._run_thread_pause_event.wait()
            elif self._status == 1:
                self._cracker.osc_force()
                self._last_waves = self._get_waves()
                time.sleep(self._interval)
            elif self._status == 2:
                while self._status == 2:
                    self._cracker.osc_single()
                    if self._cracker.osc_is_triggered():
                        self._last_waves = self._get_waves()
                        self.stop()
                    time.sleep(self._trigger_judge_wait_time)
            elif self._status == 3:
                self._cracker.osc_single()
                trigger_jude_start_time = time.time()
                while self._status == 3:
                    if time.time() - trigger_jude_start_time > self._repeat_interval:
                        self._cracker.osc_force()
                    else:
                        if self._cracker.osc_is_triggered():
                            self._last_waves = self._get_waves()
                            break
                        time.sleep(self._trigger_judge_wait_time)
                self._last_waves = self._get_waves()
            else:
                self._logger.error(f"scope_acquisition error: {self._status}")

    def _get_waves(self):
        config = self._cracker.get_current_config()
        if config.osc_analog_channel_enable is None:
            raise Exception("Channel info can't be none.")
        enable_channels = [k for k, v in config.osc_analog_channel_enable.items() if v]
        wave_dict = {}
        for c in enable_channels:
            status, wave = self._cracker.osc_get_analog_wave(
                c, self._offset, self._cracker.get_current_config().osc_sample_length
            )
            if status == protocol.STATUS_OK:
                wave_dict[c] = wave
            else:
                del wave_dict[c]
        return wave_dict

    def get_last_wave(self) -> dict[int, np.ndarray]:
        return self._last_waves
