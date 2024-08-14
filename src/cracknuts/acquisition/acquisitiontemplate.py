import abc
import datetime
import struct
import sys
import threading
import time
import typing

import numpy as np
import zarr

from cracknuts import logger
from cracknuts.cracker.abs_cracker import AbsCracker


class AcquisitionTemplate(abc.ABC):

    def __init__(self, cracker: AbsCracker | None = None):
        self._logger = logger.get_logger(self)
        self._last_wave: np.ndarray | None = np.array([np.zeros(1000)])
        self._running = False
        self._trace_count = 1
        self._on_wave_loaded_callback: typing.Callable = typing.Callable[[np.ndarray], None]
        self._trigger_judge_wait_time: float = 0.2  # second
        self._trigger_judge_timeout: float = 2000000  # microsecond
        self._run_thread = None

        self.cracker: AbsCracker = cracker

    def set_cracker(self, cracker: AbsCracker):
        self.cracker = cracker

    def on_wave_loaded(self, callback: typing.Callable[[np.ndarray], None]) -> None:
        self._on_wave_loaded_callback = callback

    def run(self, count=1):
        self._logger.debug('Start run mode.')
        self._run(save_data=True, count=count)

    def run_sync(self, count=1):
        try:
            self._do_run(save_data=True, count=count)
            self._logger.debug('stop by timeout.')
            self.stop()
        except KeyboardInterrupt:
            self._logger.debug('stop by interrupted.')
            self.stop()

    def test(self, count=1):
        self._logger.debug('Start test mode.')
        self._run(count=count)

    def stop(self):
        self._running = False

    def _run(self, save_data: bool = False, count=1):
        self._run_thread = threading.Thread(target=self._do_run, kwargs={'save_data': save_data, 'count': count})
        self._run_thread.start()

    def _do_run(self, save_data: bool = False, count=1):

        self._running = True
        # self.connect_scrat()
        # self.config_cracker()
        # self.connect_scrat()
        # self.config_scrat()
        # init
        self._trace_count = count
        self.pre_init()
        self.init()  # self.transfer() 用户
        self.save_dataset()
        self.post_init()

        self._loop()

        self.pre_finish()
        self.finish()
        if save_data:
            self.save_data()
        self.post_finish()

        self._running = True

    def _loop(self):
        for i in range(self._trace_count):
            if not self._running:
                break
            self._logger.debug('Get wave data: %s', i)
            self.pre_do()
            start = datetime.datetime.now()
            self.do()
            print('count: ', i, 'delay: ', datetime.datetime.now() - start)
            # trigger_judge_start_time = datetime.datetime.now().microsecond
            # while self._running:
            #     trigger_judge_time = datetime.datetime.now().microsecond - trigger_judge_start_time
            #     if trigger_judge_time > self._trigger_judge_timeout:
            #         self._logger.error("Triggered judge timeout and will get next waves, "
            #                            "judge time: %s and timeout is %s",
            #                            trigger_judge_time, self._trigger_judge_timeout)
            #         break
            #     self._logger.debug('Judge trigger status.')
            #     if self._is_triggered():
            #         self._last_wave = self._get_waves()
            #         if self._last_wave is not None:
            #             self._logger.debug('Got wave: %s.', self._last_wave.shape)
            #         if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
            #             try:
            #                 self._on_wave_loaded_callback(self._last_wave)
            #             except Exception as e:
            #                 self._logger.error('Wave loaded event callback error: %s', e.args)
            #         time.sleep(1)  # test
            #         break
            #     break
            # time.sleep(self._trigger_judge_wait_time)
            # self._save_wave()
            # self._post_do()

    def _loop_without_log(self):
        for i in range(self._trace_count):
            # print('yes', self._logger.handlers[0].stream)
            # self._logger.debug('Get wave data: %s', i)
            self.pre_do()
            self.do()
            trigger_judge_start_time = datetime.datetime.now().microsecond
            while self._running:
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
        # for test
        time.sleep(0.1)
        return True

    def _get_waves(self):
        return self.cracker.scrat_get_analog_wave(1, 0, 1000)

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

    def get_last_wave(self):
        return self._last_wave

    @staticmethod
    def builder():
        return AcquisitionBuilder()


class AcquisitionBuilder:

    def __init__(self):
        self._cracker = None
        self._do_function = lambda _: ...
        self._init_function = lambda _: ...

    def cracker(self, cracker: AbsCracker):
        self._cracker = cracker
        return self

    def init(self, init_function: typing.Callable[[AbsCracker], None]):
        if init_function:
            self._init_function = init_function
        return self

    def do(self, do_function: typing.Callable[[AbsCracker], None]):
        if do_function:
            self._do_function = do_function
        return self

    def build(self):
        if self._cracker is None:
            raise ValueError('No cracker')

        builder_self = self

        class AnonymousAcquisition(AcquisitionTemplate):

            def init(self):
                builder_self._init_function(self.cracker)

            def do(self):
                builder_self._do_function(self.cracker)

        return AnonymousAcquisition(builder_self._cracker)
