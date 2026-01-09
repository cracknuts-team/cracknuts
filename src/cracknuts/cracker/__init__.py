# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.cracker.cracker_g1 import CrackerG1


def cracker_s1(
        address: tuple | str,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None
):
    """
    :param address: Cracker 设备地址，可以是：
                        - IP 和端口的元组 `(ip, port)`
                        - 字符串 `"[cnp://]<ip>[:port]"`
                    例如：
                        - "192.168.0.10"
                        - "cnp://192.168.0.10:9761"
                        - (192.168.0.10, 9761)
    :type address: str | tuple | None
    :param bin_server_path: bin_server（固件）文件的路径，用于更新；通常情况下用户不需要指定。
    :type bin_server_path: str | None
    :param bin_bitstream_path: bin_bitstream（固件）文件的路径，用于更新；通常情况下用户不需要指定。
    :type bin_bitstream_path: str | None
    """
    return CrackerS1(address, bin_server_path, bin_bitstream_path)


def cracker_g1(
        address: tuple | str,
        bin_server_path: str | None = None,
        bin_bitstream_path: str | None = None
):
    """
    :param address: Cracker 设备地址，可以是：
                        - IP 和端口的元组 `(ip, port)`
                        - 字符串 `"[cnp://]<ip>[:port]"`
                    例如：
                        - "192.168.0.10"
                        - "cnp://192.168.0.10:9761"
                        - (192.168.0.10, 9761)
    :type address: str | tuple | None
    :param bin_server_path: bin_server（固件）文件的路径，用于更新；通常情况下用户不需要指定。
    :type bin_server_path: str | None
    :param bin_bitstream_path: bin_bitstream（固件）文件的路径，用于更新；通常情况下用户不需要指定。
    :type bin_bitstream_path: str | None
    """
    return CrackerG1(address, bin_server_path, bin_bitstream_path)


__all__ = ["cracker_s1", "cracker_g1"]
