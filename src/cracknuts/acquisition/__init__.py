# Copyright 2024 CrackNuts. All rights reserved.

import typing

from cracknuts.acquisition.acquisition import Acquisition
from cracknuts.acquisition.glitch_acquisition import GlitchAcquisition
from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.cracker.cracker_g1 import CrackerG1


def simple_acq(
        cracker: CrackerS1,
        init_func: typing.Callable[[CrackerS1], None] = lambda cracker: None,
        do_func: typing.Callable[[CrackerS1, int], dict[str, bytes]] = lambda cracker, count: {},
        finish_func: typing.Callable[[CrackerS1], None] = lambda cracker: None,
        **kwargs,
) -> 'Acquisition':
    """
    创建一个简单的Acquisition子类实例。

    :param cracker: Cracker实例
    :type cracker: CrackerS1
    :param init_func:
        初始化函数，该函数接受一个CrackerS1实例作为参数，用于在采集开始前进行初始化操作。
        参数说明：
            - cracker: (CrackerS1) Cracker实例
            - 返回值：无
        示例：
            cracker.nut_voltage_enable()
            cracker.nut_voltage(3.3)
            cracker.nut_clock_enable()
            cracker.nut_clock_freq('8M')
            cracker.uart_io_enable()
            status, ret = cracker.uart_transmit_receive(cmd_set_aes_enc_key + aes_key, timeout=1000, rx_count=6)
    :type init_func: typing.Callable[[CrackerS1], None]
    :param do_func:
        执行函数，具体的采集逻辑实现，该函数接受一个CrackerS1实例和当前采集计数作为参数，返回一个包含采集数据的字典。
        参数说明：
            - cracker: (CrackerS1) Cracker实例
            - count: (int) 当前采集计数，从0开始
            - 返回值：dict[str, bytes]，包含采集数据的字典，格式如下：
              {
                  "plaintext": 明文数据的字节串,
                  "ciphertext": 密文数据的字节串,
                  "key": 密钥数据的字节串（可选）,
                  "extended": 扩展数据的字节串（可选）,
              }
        示例：
            def do_func(cracker: CrackerS1, count: int) -> dict[str, bytes]:
                plaintext = random.randbytes(aes_data_len)
                status, ciphertext = cracker.uart_transmit_receive(cmd_aes_enc + plaintext_data, rx_count= 12)
                return {
                    "plaintext": plaintext,
                    "ciphertext": ciphertext,
                    "key": aes_key,
                }
    :type do_func: typing.Callable[[CrackerS1, int], dict[str, bytes]]
    :param finish_func:
        结束后处理函数，该函数接受一个CrackerS1实例作为参数，用于在采集结束后进行清理操作。
        参数说明：
            - cracker: (CrackerS1) Cracker实例
            - 返回值：无
        示例：
            def finish_func(cracker: CrackerS1) -> None:
                cracker.nut_voltage_disable()
                cracker.nut_clock_disable()
                cracker.uart_io_disable()
    :type finish_func: typing.Callable[[CrackerS1], None]
    :param kwargs: 其他Acquisition的关键字参数
    :type kwargs: dict
    :return: Acquisition实例
    """

    class AnonymousAcquisition(Acquisition):
        def __init__(self, **_kwargs):
            _kwargs['cracker'] = cracker
            super().__init__(**_kwargs)

        def init(self):
            init_func(cracker)

        def do(self, count: int):
            return do_func(cracker, count)

        def finish(self):
            finish_func(cracker)

    return AnonymousAcquisition(**kwargs)


def simple_glitch_acq(
        cracker: CrackerG1,
        init_func: typing.Callable[[CrackerG1], None] = lambda cracker: None,
        do_func: typing.Callable[[CrackerG1, int], dict[str, bytes]] = lambda cracker, count: {},
        finish_func: typing.Callable[[CrackerG1], None] = lambda cracker: None, **kwargs) -> GlitchAcquisition:
    """
    创建一个简单的GlitchAcquisition子类实例。

    :param cracker: Cracker实例
    :type cracker: CrackerG1
    :param init_func:
        初始化函数，该函数接受一个CrackerG1实例作为参数，用于在采集开始前进行初始化操作。
        参数说明：
            - cracker: (CrackerG1) Cracker实例
            - 返回值：无
        示例：
            cracker.nut_voltage_enable()
            cracker.nut_voltage(3.3)
            cracker.nut_clock_enable()
            cracker.nut_clock_freq('8M')
            cracker.uart_io_enable()
            status, ret = cracker.uart_transmit_receive(cmd_set_aes_enc_key + aes_key, timeout=1000, rx_count=6)
    :type init_func: typing.Callable[[CrackerG1], None]
    :param do_func:
        执行函数，具体的采集逻辑实现，该函数接受一个CrackerG1实例和当前采集计数作为参数，返回一个包含采集数据的字典。
        参数说明：
            - cracker: (CrackerG1) Cracker实例
            - count: (int) 当前采集计数，从0开始
            - 返回值：dict[str, bytes]，包含采集数据的字典，格式如下：
              {
                  "plaintext": 明文数据的字节串,
                  "ciphertext": 密文数据的字节串,
                  "key": 密钥数据的字节串（可选）,
                  "extended": 扩展数据的字节串（可选）,
              }
        示例：
            def do_func(cracker: CrackerG1, count: int) -> dict[str, bytes]:
                plaintext = random.randbytes(aes_data_len)
                status, ciphertext = cracker.uart_transmit_receive(cmd_aes_enc + plaintext_data, rx_count= 12)
                return {
                    "plaintext": plaintext,
                    "ciphertext": ciphertext,
                    "key": aes_key,
                }
    :type do_func: typing.Callable[[CrackerG1, int], dict[str, bytes]]
    :param finish_func:
        结束后处理函数，该函数接受一个CrackerG1实例作为参数，用于在采集结束后进行清理操作。
        参数说明：
            - cracker: (CrackerG1) Cracker实例
            - 返回值：无
        示例：
            def finish_func(cracker: CrackerG1) -> None:
                cracker.nut_voltage_disable()
                cracker.nut_clock_disable()
                cracker.uart_io_disable()
    :type finish_func: typing.Callable[[CrackerG1], None]
    :param kwargs: 其他Acquisition的关键字参数
    :type kwargs: dict
    :return: Acquisition实例
    """
    class AnonymousAcquisition(GlitchAcquisition):
        def __init__(self, **_kwargs):
            _kwargs['cracker'] = cracker
            super().__init__(**_kwargs)

        def init(self):
            init_func(cracker)

        def do(self, count: int):
            return do_func(cracker, count)

        def finish(self):
            finish_func(cracker)

    return AnonymousAcquisition(**kwargs)


__all__ = ["simple_acq", "simple_glitch_acq"]
