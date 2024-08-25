import abc
import datetime
import threading
import time
import typing

import numpy as np
from cracknuts import logger
from cracknuts.cracker.stateful_cracker import StatefulCracker


class AcqProgress:

    def __init__(self, finished, total):
        self.finished: int = finished
        self.total: int = total


class Acquisition(abc.ABC):
    _STATUS_STOPPED = 0
    _STATUS_TESTING = 1
    _STATUS_RUNNING = 2
    _STATUS_PAUSED_SWITCH = -1

    def __init__(self, cracker: StatefulCracker | None = None):
        self._logger = logger.get_logger(self)
        self._last_wave: dict[int, np.ndarray] | None = {1: np.zeros(1)}
        self._status: int = self._STATUS_STOPPED
        self._trace_count = 1
        self._trigger_judge_wait_time: float = 0.05  # second
        self._trigger_judge_timeout: float = 2000000  # microsecond
        self._run_thread_pause_event: threading.Event = threading.Event()
        self.cracker: StatefulCracker = cracker

        self._on_wave_loaded_callback: typing.Callable[[np.ndarray], None] | None = None
        self._on_status_change_listeners: typing.List[typing.Callable[[int], None]] = []
        self._on_run_progress_changed_listeners: typing.List[typing.Callable[[typing.Dict], None]] = []

    def set_cracker(self, cracker: StatefulCracker):
        self.cracker = cracker

    def on_status_changed(self, callback: typing.Callable[[int], None]) -> None:
        """
        User should not use this function. If you need to perform actions when the ACQ state changes,
        please use the node functions in the ACQ lifecycle point: `init`, `do`, and `finish`.

        status: 0 stopped, 1 testing, 2 running 3 paused
        """
        self._on_status_change_listeners.append(callback)

    def on_run_progress_changed(self, callback: typing.Callable[[typing.Dict], None]) -> None:
        self._on_run_progress_changed_listeners.append(callback)

    def on_wave_loaded(self, callback: typing.Callable[[np.ndarray], None]) -> None:
        self._on_wave_loaded_callback = callback

    def run(self, count=1):
        if self._status < 0:
            self._logger.debug('Resume to run mode.')
            self.resume()
        else:
            self._logger.debug('Start run mode.')
            self._run(test=False, count=count)

    def run_sync(self, count=1):
        try:
            self._do_run(test=False, count=count)
            self._logger.debug('stop by timeout.')
            self.stop()
        except KeyboardInterrupt:
            self._logger.debug('stop by interrupted.')
            self.stop()

    def test(self, count=-1):
        if self._status < 0:
            self._logger.debug('Resume to test mode.')
            self.resume()
        else:
            self._logger.debug('Start test mode.')
            self._run(test=True, count=count)

    def pause(self):
        self._logger.error('Status change from pause...')
        if self._status > 0:
            self._status_changed(self._STATUS_PAUSED_SWITCH)
            self._run_thread_pause_event.clear()

    def resume(self):
        self._logger.error('Status change from resume...')
        if self._status < 0:
            self._status_changed(self._STATUS_PAUSED_SWITCH)
            self._run_thread_pause_event.set()

    def stop(self):
        self._logger.error('Status change from stop...')
        if not self._run_thread_pause_event.is_set():
            self._run_thread_pause_event.set()
        self._status = self._STATUS_STOPPED

    def _run(self, test: bool = True, count=1):
        self._run_thread_pause_event.set()
        threading.Thread(target=self._do_run, kwargs={'test': test, 'count': count}).start()

    def _do_run(self, test: bool = True, count=1):

        if self._status:
            raise Exception(f'AcquisitionTemplate is already running in {'run' if not test else 'test'} mode.')

        if not test:
            self._status_changed(self._STATUS_RUNNING)
        else:
            self._status_changed(self._STATUS_TESTING)

        self._status = True
        self._trace_count = count
        self.pre_init()
        self.init()
        self.save_dataset()
        self.post_init()
        self._loop()
        self.pre_finish()
        self.finish()
        if not test:
            self.save_data()
        self.post_finish()

    def _status_changed(self, status: int):
        self._logger.error(f'Status changed: {status}.')
        if status < 0:
            self._status = self._status * status
        else:
            self._status = status
        for listener in self._on_status_change_listeners:
            listener(self._status)

    def _loop(self):
        i = 0
        while self._status != 0 and self._trace_count - i != 0:
            self._run_thread_pause_event.wait()
            self._logger.debug('Get wave data: %s', i)
            self.pre_do()
            start = datetime.datetime.now()
            self.do()
            self._logger.debug('count: ', i, 'delay: ', datetime.datetime.now() - start)
            trigger_judge_start_time = datetime.datetime.now().microsecond
            while self._status != 0:
                trigger_judge_time = datetime.datetime.now().microsecond - trigger_judge_start_time
                if trigger_judge_time > self._trigger_judge_timeout:
                    self._logger.error("Triggered judge timeout and will get next waves, "
                                       "judge time: %s and timeout is %s",
                                       trigger_judge_time, self._trigger_judge_timeout)
                    break
                self._logger.debug('Judge trigger status.')
                if self._is_triggered():
                    self._last_wave = self._get_waves(self.cracker.get_config_scrat_offset(),
                                                      self.cracker.get_config_scrat_sample_count())
                    if self._last_wave is not None:
                        # self._logger.debug('Got wave: %s.', {k: v.shape for k, v in self._last_wave.items()})
                        self._logger.debug('Got wave: %s.', self._last_wave)
                    if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
                        try:
                            self._on_wave_loaded_callback(self._last_wave)
                        except Exception as e:
                            self._logger.error('Wave loaded event callback error: %s', e.args)
                    break
                break
            time.sleep(self._trigger_judge_wait_time)
            self._save_wave()
            self._post_do()
            i += 1
            self._progress_changed(AcqProgress(i, self._trace_count))
        self._logger.error(f'status change in loop...{self._status }')
        self._status_changed(self._STATUS_STOPPED)

    def _progress_changed(self, progress: 'AcqProgress'):
        for listener in self._on_run_progress_changed_listeners:
            listener({'finished': progress.finished, 'total': progress.total})

    def _loop_without_log(self):
        for i in range(self._trace_count):
            # print('yes', self._logger.handlers[0].stream)
            # self._logger.debug('Get wave data: %s', i)
            self.pre_do()
            self.do()
            trigger_judge_start_time = datetime.datetime.now().microsecond
            while self._status:
                trigger_judge_time = datetime.datetime.now().microsecond - trigger_judge_start_time
                if trigger_judge_time > self._trigger_judge_timeout:
                    # self._logger.error("Triggered judge timeout and will get next waves, "
                    #                    "judge time: %s and timeout is %s",
                    #                    trigger_judge_time, self._trigger_judge_timeout)
                    break
                # self._logger.debug('Judge trigger status.')
                if self._is_triggered():
                    self._last_wave = self._get_waves()
                    if self._last_wave is not None:
                        ...
                        # self._logger.debug('Got wave: %s.', self._last_wave.shape)
                    if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
                        try:
                            self._on_wave_loaded_callback(self._last_wave)
                        except Exception as e:
                            ...
                            # self._logger.error('Wave loaded event callback error: %s', e.args)
                    time.sleep(1)
                    break
                time.sleep(self._trigger_judge_wait_time)
            self._save_wave()
            self._post_do()

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

    def connect_net(self):
        ...

    def config_scrat(self):
        ...

    def config_cracker(self):
        ...

    def pre_init(self):
        ...

    @abc.abstractmethod
    def init(self):
        ...

    def post_init(self):
        ...

    def transfer(self):
        ...

    def pre_do(self):
        ...

    @abc.abstractmethod
    def do(self):
        ...

    def _post_do(self):
        ...

    def arm(self):
        ...

    def _is_triggered(self):
        return self.cracker.scrat_is_triggered()

    def _get_waves(self, offset: int, sample_count: int) -> typing.Dict[int, np.ndarray]:
        enable_channels = self.cracker.get_config_scrat_enable_channels()
        wave_dict = {}
        for c in enable_channels:
            wave_dict[c] = self.cracker.scrat_get_analog_wave(c, offset, sample_count)
        return wave_dict

    def _save_wave(self):
        ...

    def save_data(self, data_type: str = 'zarr'):
        """
        Save wave, key and other info to acquisition dataset file.
        """
        # if data_type == 'zarr':
        #     zarr.create()
        ...

    def pre_finish(self):
        ...

    def post_finish(self):
        ...

    def save_dataset(self):
        ...

    def finish(self):
        pass

    def get_last_wave(self) -> typing.Dict[int, np.ndarray]:
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
        if init_function:
            self._init_function = init_function
        return self

    def do(self, do_function: typing.Callable[[StatefulCracker], None]):
        if do_function:
            self._do_function = do_function
        return self

    def build(self):
        if self._cracker is None:
            raise ValueError('No cracker')

        builder_self = self

        class AnonymousAcquisition(Acquisition):

            def init(self):
                builder_self._init_function(self.cracker)

            def do(self):
                builder_self._do_function(self.cracker)

        return AnonymousAcquisition(builder_self._cracker)
