import abc

from nutcracker import logger
from nutcracker.cracker.abs_cracker import AbsCracker


class Acquisition(abc.ABC):

    def __init__(self, cracker: AbsCracker):
        self._logger = logger.get_logger(self)
        self._cracker = cracker

    def start(self):
        ...

    def test(self):
        self.connect_scrat()
        self.config_cracker()
        self.connect_scrat()
        self.config_scrat()
        # init
        self.hook_pre_init()
        self.hook_init() # self.transfer() 用户
        self.save_dataset()
        self.hook_post_init()
        # loop
        for i in range(10):
            self.hook_pre_loop()
            self.loop()
            self.show_wave() # 展示波形
            # self.save_wave()
            # self.save_data()
            self.hook_post_loop()

        self.hook_pre_finish()
        self.finish()
        self.save_data()
        self.hook_post_finish()


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

    def hook_pre_init(self):
        ...

    def hook_post_init(self):
        ...

    def transfer(self):
        ...

    def hook_pre_loop(self):
        ...

    def hook_post_loop(self):
        ...

    def arm(self):
        ...

    def is_triggered(self):
        ...

    def get_waves(self):
        ...

    def save_wave(self):
        ...

    def save_data(self):
        ...

    def hook_pre_finish(self):
        ...

    def hook_post_finish(self):
        ...

    def save_dataset(self):
        ...

    def loop(self):
        ...
