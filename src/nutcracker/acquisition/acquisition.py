import abc
import datetime
import threading
import time
import typing

import numpy as np
from nutcracker import logger
from nutcracker.cracker.abs_cracker import AbsCracker


class Acquisition(abc.ABC):

    def __init__(self, cracker: AbsCracker):
        self._logger = logger.get_logger(self)
        self._cracker = cracker
        self._last_wave: np.ndarray | None = None
        self._running = False
        self._trace_count = 500
        self._on_wave_loaded_callback: typing.Callable = typing.Callable[[np.ndarray], None]
        self._trigger_judge_wait_time: float = 0.01  # second
        self._trigger_judge_timeout: float = 2000000  # microsecond

    def on_wave_loaded(self, callback: typing.Callable[[np.ndarray], None]) -> None:
        self._on_wave_loaded_callback = callback

    def start(self):
        self._run()
        self.save_data()

    def test(self):
        self._run()

    def stop(self):
        self._running = False

    def _run(self):
        threading.Thread(target=self._do_run).start()

    def _do_run(self):

        self._running = True
        self.connect_scrat()
        self.config_cracker()
        self.connect_scrat()
        self.config_scrat()
        # init
        self.pre_init()
        self.init()  # self.transfer() 用户
        self.save_dataset()
        self.post_init()

        self._loop()

        self.pre_finish()
        self.finish()
        self.save_data()
        self.post_finish()

        self._running = True

    def _loop(self):
        for i in range(self._trace_count):
            self._logger.debug('Get wave data: %s', i)
            self.pre_do()
            self.do()
            trigger_judge_start_time = datetime.datetime.now().microsecond
            while self._running:
                trigger_judge_time = datetime.datetime.now().microsecond - trigger_judge_start_time
                if trigger_judge_time > self._trigger_judge_timeout:
                    self._logger.error("Triggered judge timeout and will get next waves, "
                                       "judge time: %s and timeout is %s",
                                       trigger_judge_time, self._trigger_judge_timeout)
                    break
                self._logger.debug('Judge trigger status.')
                if self._is_triggered():
                    self._last_wave = self._get_waves()
                    self._logger.debug('Get wave: %s.', self._last_wave.shape)
                    if self._on_wave_loaded_callback and callable(self._on_wave_loaded_callback):
                        try:
                            self._on_wave_loaded_callback(self._last_wave)
                        except Exception as e:
                            self._logger.error('Wave loaded event callback error: %s', e.args)
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
        self._cracker.connect()

    def connect_net(self):
        ...

    def config_scrat(self):
        ...

    def config_cracker(self):
        ...

    def pre_init(self):
        ...

    def init(self):
        ...

    def post_init(self):
        ...

    def transfer(self):
        ...

    def pre_do(self):
        ...

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
        return np.array([np.random.random(1000)])

    def _save_wave(self):
        ...

    def save_data(self):
        """
        Save wave, key and other info to acquisition dataset file.
        """
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
