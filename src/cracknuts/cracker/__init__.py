# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.cracker.cracker_g1 import CrackerG1
from cracknuts.cracker.cracker_f1 import CrackerF1


import warnings


def new_cracker(
    address: tuple[str, int] | str,
    bin_server_path: str | None = None,
    bin_bitstream_path: str | None = None,
    model: str | None = None,
):
    """
    Deprecated.

    This function is deprecated and disabled.
    Its dynamic return type prevents IDEs and static type checkers from providing
    accurate code completion and type hints.

    Users must explicitly create cracker instances using one of the following
    functions instead:

        - cracker_s1(...)
        - cracker_g1(...)

    :param address: Cracker device address. Supported formats include:
                       - A tuple ``(ip, port)``
                       - A string in the form ``"[cnp://]<ip>[:port]"``

                   Examples:
                       - ``"192.168.0.10"``
                       - ``"cnp://192.168.0.10:9761"``
                       - ``("192.168.0.10", 9761)``
    :type address: str | tuple | None
    :param bin_server_path: Path to the ``bin_server`` firmware image used for device update.
                            In most cases, users do not need to specify this parameter.
    :type bin_server_path: str | None
    :param bin_bitstream_path: Path to the ``bin_bitstream`` firmware image used for device update.
                               In most cases, users do not need to specify this parameter.
    :type bin_bitstream_path: str | None
    :param model: Cracker model. Supported values are:
                      - ``"s1"``: for Cracker S1
                      - ``"g1"``: for Cracker G1

                  If not specified, defaults to ``"s1"``.
    :type model: str | None
    """

    warnings.warn(
        "new_cracker() is deprecated and has been disabled. " "Use cracker_s1(...) or cracker_g1(...) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    kwargs = {"address": address, "bin_server_path": bin_server_path, "bin_bitstream_path": bin_bitstream_path}
    if model is None:
        model = CrackerS1
    else:
        if isinstance(model, str):
            if model.lower() == "s1":
                model = CrackerS1
            elif model.lower() == "g1":
                model = CrackerG1
            else:
                raise ValueError(f"Unknown cracker model: {model}")
    return model(**kwargs)


def cracker_s1(
    address: tuple | str, bin_server_path: str | None = None, bin_bitstream_path: str | None = None
) -> CrackerS1:
    """
    Creates and returns a :class:`CrackerS1` instance.

    :param address: Cracker device address. Supported formats include:
                       - A tuple ``(ip, port)``
                       - A string in the form ``"[cnp://]<ip>[:port]"``

                   Examples:
                       - ``"192.168.0.10"``
                       - ``"cnp://192.168.0.10:9761"``
                       - ``("192.168.0.10", 9761)``
    :type address: str | tuple | None
    :param bin_server_path: Path to the ``bin_server`` firmware image used for device update.
                            In most cases, users do not need to specify this parameter.
    :type bin_server_path: str | None
    :param bin_bitstream_path: Path to the ``bin_bitstream`` firmware image used for device update.
                               In most cases, users do not need to specify this parameter.
    :type bin_bitstream_path: str | None
    """
    return CrackerS1(address, bin_server_path, bin_bitstream_path)


def cracker_g1(
    address: tuple | str, bin_server_path: str | None = None, bin_bitstream_path: str | None = None
) -> CrackerG1:
    """
    Creates and returns a :class:`CrackerG1` instance.

    :param address: Cracker device address. Supported formats include:
                       - A tuple ``(ip, port)``
                       - A string in the form ``"[cnp://]<ip>[:port]"``

                   Examples:
                       - ``"192.168.0.10"``
                       - ``"cnp://192.168.0.10:9761"``
                       - ``("192.168.0.10", 9761)``
    :type address: str | tuple | None
    :param bin_server_path: Path to the ``bin_server`` firmware image used for device update.
                            In most cases, users do not need to specify this parameter.
    :type bin_server_path: str | None
    :param bin_bitstream_path: Path to the ``bin_bitstream`` firmware image used for device update.
                               In most cases, users do not need to specify this parameter.
    :type bin_bitstream_path: str | None
    """

    return CrackerG1(address, bin_server_path, bin_bitstream_path)


def cracker_f1(
    address: tuple | str, bin_server_path: str | None = None, bin_bitstream_path: str | None = None
) -> CrackerF1:
    """
    Creates and returns a :class:`CrackerG1` instance.

    :param address: Cracker device address. Supported formats include:
                       - A tuple ``(ip, port)``
                       - A string in the form ``"[cnp://]<ip>[:port]"``

                   Examples:
                       - ``"192.168.0.10"``
                       - ``"cnp://192.168.0.10:9761"``
                       - ``("192.168.0.10", 9761)``
    :type address: str | tuple | None
    :param bin_server_path: Path to the ``bin_server`` firmware image used for device update.
                            In most cases, users do not need to specify this parameter.
    :type bin_server_path: str | None
    :param bin_bitstream_path: Path to the ``bin_bitstream`` firmware image used for device update.
                               In most cases, users do not need to specify this parameter.
    :type bin_bitstream_path: str | None
    """
    return CrackerF1(address, bin_server_path, bin_bitstream_path)


__all__ = ["new_cracker", "cracker_s1", "cracker_g1", "cracker_f1"]
