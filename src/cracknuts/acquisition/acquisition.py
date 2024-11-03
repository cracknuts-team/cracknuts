# Copyright 2024 CrackNuts. All rights reserved.

import abc
import datetime
import threading
import time
import typing

import numpy as np

from cracknuts import logger
from cracknuts.cracker.stateful_cracker import StatefulCracker
from cracknuts.solver.trace import ScarrTraceDataset, NumpyTraceDataset


class AcqProgress:
    def __init__(self, finished: int, total: int):
        self.finished: int = finished
        self.total: int = total


class Acquisition(abc.ABC):
    STATUS_STOPPED: int = 0
    STATUS_TESTING: int = 1
    STATUS_RUNNING: int = 2
    _STATUS_PAUSED_SWITCH: int = -1

    DO_ERROR_HANDLER_STRATEGY_EXIT: int = 0
    DO_ERROR_HANDLER_STRATEGY_CONTINUE_UNTIL_MAX_ERROR_COUNT: int = 1

    def __init__(
        self,
        cracker: StatefulCracker,
        trace_count: int = 1000,
        sample_length: int = 1024,
        sample_offset: int = 0,
        data_length: int = 0,
        trigger_judge_wait_time: float = 0.05,
        trigger_judge_timeout: float = 1.0,
        do_error_handler_strategy: int = DO_ERROR_HANDLER_STRATEGY_EXIT,
        do_error_max_count: int = -1,
        file_format: str = "scarr",
        file_path: str = "auto",
    ):
        self._logger = logger.get_logger(self)
        self._last_wave: dict[int, np.ndarray] | None = {1: np.zeros(1)}
        self._status: int = self.STATUS_STOPPED
        self._current_trace_count = 1
        self._run_thread_pause_event: threading.Event = threading.Event()

        self.cracker: StatefulCracker = cracker
        self.trace_count: int = trace_count
        self.sample_length = sample_length
        self.sample_offset: int = sample_offset
        self.data_length: int = data_length
        self.trigger_judge_wait_time: float = trigger_judge_wait_time  # second
        self.trigger_judge_timeout: float = trigger_judge_timeout  # second
        self.do_error_handler_strategy: int = do_error_handler_strategy
        self.do_error_max_count: int = do_error_max_count  # -1 never exit
        self.file_format: str = file_format
        self.file_path: str = file_path

        self._on_wave_loaded_callback: typing.Callable[[typing.Any], None] | None = None
        self._on_status_change_listeners: list[typing.Callable[[int], None]] = []
        self._on_run_progress_changed_listeners: list[typing.Callable[[dict], None]] = []

    def get_status(self):
        return self._status

    def set_cracker(self, cracker: StatefulCracker):
        self.cracker = cracker

    def on_status_changed(self, callback: typing.Callable[[int], None]) -> None:
        """
        User should not use this function. If you need to perform actions when the ACQ state changes,
        please use the node functions in the ACQ lifecycle point: `init`, `do`, and `finish`.

        status: 0 stopped, 1 testing, 2 running 3 paused
        """
        self._on_status_change_listeners.append(callback)

    def on_run_progress_changed(self, callback: typing.Callable[[dict], None]) -> None:
        self._on_run_progress_changed_listeners.append(callback)

    def on_wave_loaded(self, callback: typing.Callable[[typing.Any], None]) -> None:
        self._on_wave_loaded_callback = callback

    def run(
        self,
        count: int = 1,
        sample_length: int = 1024,
        sample_offset: int = 0,
        data_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "scarr",
        file_path: str | None = "auto",
    ):
        if self._status < 0:
            self.resume()
        else:
            self._run(
                test=False,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                data_length=data_length,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
                file_format=file_format,
                file_path=file_path,
            )

    def run_sync(
        self,
        count=1,
        sample_length: int = 1024,
        sample_offset: int = 0,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "scarr",
    ):
        try:
            self._do_run(
                test=False,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
                file_format=file_format,
            )
            self._logger.debug("stop by timeout.")
        except KeyboardInterrupt:
            self._logger.debug("stop by interrupted.")
            self.stop()

    def test(
        self,
        count=-1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
    ):
        if self._status < 0:
            self._logger.debug("Resume to test mode.")
            self.resume()
        else:
            self._logger.debug("Start test mode.")
            self._run(
                test=True,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
            )

    def test_sync(
        self,
        count=-1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
    ):
        try:
            self._do_run(
                test=True,
                count=count,
                sample_length=sample_length,
                sample_offset=sample_offset,
                trigger_judge_wait_time=trigger_judge_wait_time,
                trigger_judge_timeout=trigger_judge_timeout,
                do_error_max_count=do_error_max_count,
                do_error_handler_strategy=do_error_handler_strategy,
            )
        except KeyboardInterrupt:
            self._logger.debug("stop by interrupted.")
            self.stop()

    def pause(self):
        if self._status > 0:
            self._run_thread_pause_event.clear()
            self._status = self._status * self._STATUS_PAUSED_SWITCH

    def resume(self):
        if self._status < 0:
            self._run_thread_pause_event.set()
            self._status = self._status * self._STATUS_PAUSED_SWITCH

    def stop(self):
        if not self._run_thread_pause_event.is_set():
            self._run_thread_pause_event.set()
        self._status = self.STATUS_STOPPED

    def _run(
        self,
        test: bool = True,
        count: int = 1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        data_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "scarr",
        file_path: str | None = "auto",
    ):
        self._run_thread_pause_event.set()
        threading.Thread(
            target=self._do_run,
            kwargs={
                "test": test,
                "count": count,
                "sample_length": sample_length,
                "sample_offset": sample_offset,
                "data_length": data_length,
                "trigger_judge_wait_time": trigger_judge_wait_time,
                "trigger_judge_timeout": trigger_judge_timeout,
                "do_error_max_count": do_error_max_count,
                "do_error_handler_strategy": do_error_handler_strategy,
                "file_format": file_format,
                "file_path": file_path,
            },
        ).start()

    def _do_run(
        self,
        test: bool = True,
        count: int = 1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        data_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "scarr",
        file_path: str | None = "auto",
    ):
        if self._status > 0:
            raise Exception(f'AcquisitionTemplate is already running in {'run' if self._status == 2 else 'test'} mode.')

        if not test:
            self._status = self.STATUS_RUNNING
            self._status_changed()
        else:
            self._status = self.STATUS_TESTING
            self._status_changed()

        self.trace_count = count
        if sample_length is not None:
            self.sample_length = sample_length
        if sample_offset is not None:
            self.sample_offset = sample_offset
        if data_length is not None:
            self.data_length = data_length
        if trigger_judge_wait_time is not None:
            self.trigger_judge_wait_time = trigger_judge_wait_time
        if trigger_judge_timeout is not None:
            self.trigger_judge_timeout = trigger_judge_timeout
        if do_error_max_count is not None:
            self.do_error_max_count = do_error_max_count
        if do_error_handler_strategy is not None:
            self.do_error_handler_strategy = do_error_handler_strategy
        if file_format is not None:
            self.file_format = file_format
        if file_path is not None:
            self.file_path = file_path
        self.pre_init()
        self.init()
        self._post_init()
        self._loop(not test, self.file_path, self.file_format)
        self._pre_finish()
        self._finish()
        self._post_finish()

    def _status_changed(self):
        for listener in self._on_status_change_listeners:
            listener(self._status)

    def _loop(self, persistent: bool = True, file_path: str | None = None, file_format: str = "scarr"):
        do_error_count = 0
        trace_index = 0
        self._progress_changed(AcqProgress(trace_index, self.trace_count))

        cracker_version = self.cracker.get_version()
        if persistent:
            if file_path is None or file_path == "auto":
                file_path = "./dataset/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                if file_format == "scarr":
                    file_path += ".zarr"
                elif file_format == "numpy":
                    file_path += ".npy"

            if file_format == "scarr":
                dataset = ScarrTraceDataset.new(
                    file_path,
                    1,
                    self.trace_count,
                    self.sample_length,
                    self.data_length,
                    version=f"({cracker_version}, {cracker_version})",
                )  # todo channel
            elif file_format == "numpy":
                dataset = NumpyTraceDataset.new(
                    file_path,
                    1,
                    self.trace_count,
                    self.sample_length,
                    self.data_length,
                    version=f"({cracker_version}, {cracker_version})",
                )  # todo channel
            else:
                self._logger.warning(f"Unsupported file format: {file_format}")
        else:
            dataset = None

        while self._status != 0 and self.trace_count - trace_index != 0:
            if self._status < 0:
                self._status_changed()
                self._run_thread_pause_event.wait()
                self._status_changed()
            self._logger.debug("Get wave data: %s", trace_index)
            self.pre_do()
            start = time.time()
            try:
                data = self.do()
            except Exception as e:
                self._logger.error("Do error: %s", e.args)
                do_error_count += 1
                if self.do_error_handler_strategy == self.DO_ERROR_HANDLER_STRATEGY_EXIT:
                    self._logger.error("Exit with do error")
                elif do_error_count > self.do_error_max_count:
                    self._logger.error(
                        f"Exit with do function get error count: {do_error_count} is grate than do_error_max_count"
                    )
                    break
                else:
                    self._logger.error(f"Do function get error count: {do_error_count}")
                    continue
            self._logger.debug(f"count: {trace_index} delay: {time.time() - start}")
            trigger_judge_start_time = time.time()
            while self._status != 0:
                trigger_judge_time = time.time() - trigger_judge_start_time
                if trigger_judge_time > self.trigger_judge_timeout:
                    self._logger.error(
                        "Triggered judge timeout and will get next waves, " "judge time: %s and timeout is %s",
                        trigger_judge_time,
                        self.trigger_judge_timeout,
                    )
                    break
                self._logger.debug("Judge trigger status.")
                # if self._is_triggered():
                if True:
                    self._last_wave = self._get_waves(self.sample_offset, self.sample_length)
                    if self._last_wave is not None:
                        self._logger.debug(
                            "Got wave: %s.",
                            {k: v.shape for k, v in self._last_wave.items()},
                        )
                        # self._logger.debug('Got wave: ')
                    if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
                        try:
                            self._on_wave_loaded_callback(self._last_wave)
                        except Exception as e:
                            self._logger.error("Wave loaded event callback error: %s", e.args)
                    break

                time.sleep(self.trigger_judge_wait_time)
            if dataset is not None and self._last_wave is not None:
                dataset.set_trace(0, trace_index, self._last_wave[1], np.frombuffer(data, dtype=np.uint8))
                # dataset.set_trace(1, trace_index, self._last_wave[2], data)  # todo second channel
            self._post_do()
            trace_index += 1
            self._current_trace_count = trace_index
            self._progress_changed(AcqProgress(trace_index, self.trace_count))

        if dataset is not None:
            dataset.dump()
        self._status = self.STATUS_STOPPED
        self._status_changed()

    def _progress_changed(self, progress: "AcqProgress"):
        for listener in self._on_run_progress_changed_listeners:
            listener({"finished": progress.finished, "total": progress.total})

    def _loop_without_log(self):
        ...
        # for i in range(self.trace_count):
        #     # print('yes', self._logger.handlers[0].stream)
        #     # self._logger.debug('Get wave data: %s', i)
        #     self.pre_do()
        #     self.do()
        #     trigger_judge_start_time = time.time()
        #     while self._status:
        #         trigger_judge_time = time.time() - trigger_judge_start_time
        #         if trigger_judge_time > self.trigger_judge_timeout:
        #             # self._logger.error("Triggered judge timeout and will get next waves, "
        #             #                    "judge time: %s and timeout is %s",
        #             #                    trigger_judge_time, self._trigger_judge_timeout)
        #             break
        #         # self._logger.debug('Judge trigger status.')
        #         if self._is_triggered():
        #             self._last_wave = self._get_waves()
        #             if self._last_wave is not None:
        #                 ...
        #                 # self._logger.debug('Got wave: %s.', self._last_wave.shape)
        #             if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
        #                 try:
        #                     self._on_wave_loaded_callback(self._last_wave)
        #                 except Exception as e:
        #                     ...
        #                     # self._logger.error('Wave loaded event callback error: %s', e.args)
        #             time.sleep(1)
        #             break
        #         time.sleep(self.trigger_judge_wait_time)
        #     self._save_wave()
        #     self._post_do()

    def connect_scrat(self):
        """
        Connect to scrat device
        :return:
        """
        ...

    def connect_cracker(self):
        """
        Connect to cracker device.
        :return:
        """
        self.cracker.connect()

    def connect_net(self): ...

    def config_scrat(self): ...

    def config_cracker(self): ...

    def pre_init(self):
        self.cracker.sync_config_to_cracker()

    @abc.abstractmethod
    def init(self): ...

    def _post_init(self): ...

    def transfer(self): ...

    def pre_do(self):
        self.cracker.osc_single()

    @abc.abstractmethod
    def do(self): ...

    def _do(self):
        try:
            self.do()
            return True
        except Exception as e:
            self._logger.error("Do error: %s", e.args)
            return False

    def _post_do(self): ...

    def _is_triggered(self):
        return self.cracker.osc_is_triggered()

    def _get_waves(self, offset: int, sample_count: int) -> dict[int, np.ndarray]:
        config = self.cracker.get_current_config()
        if config.osc_analog_channel_enable is None:
            raise Exception("Channel info can't be none.")
        enable_channels = [k for k, v in config.osc_analog_channel_enable.items() if v]
        wave_dict = {}
        for c in enable_channels:
            status, wave_dict[c] = self.cracker.osc_get_analog_wave(c, offset, sample_count)
        return wave_dict

    def save_data(self, data_type: str = "zarr"):
        """
        Save wave, key and other info to acquisition dataset file.
        """
        # if data_type == 'zarr':
        #     zarr.create()
        ...

    def _pre_finish(self): ...

    def _post_finish(self): ...

    def _save_dataset(self): ...

    def _finish(self):
        pass

    def get_last_wave(self) -> dict[int, np.ndarray] | None:
        return self._last_wave

    @staticmethod
    def builder():
        return AcquisitionBuilder()


class AcquisitionBuilder:
    def __init__(self):
        self._cracker = None
        self._do_function = lambda _: ...
        self._init_function = lambda _: ...

    def cracker(self, cracker: StatefulCracker):
        self._cracker = cracker
        return self

    def init(self, init_function: typing.Callable[[StatefulCracker], None]):
        if init_function is not None:
            self._init_function = init_function
        return self

    def do(self, do_function: typing.Callable[[StatefulCracker], None]):
        if do_function is not None:
            self._do_function = do_function
        return self

    def build(self, **kwargs):
        if self._cracker is None:
            raise ValueError("No cracker")

        builder_self = self

        class AnonymousAcquisition(Acquisition):
            def __init__(self, *ana_args, **ana_kwargs):
                super().__init__(*ana_args, **ana_kwargs)

            def init(self):
                builder_self._init_function(self.cracker)

            def do(self):
                return builder_self._do_function(self.cracker)

        return AnonymousAcquisition(self._cracker, **kwargs)
