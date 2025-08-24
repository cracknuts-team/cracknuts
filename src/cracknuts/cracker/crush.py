import struct

from cracknuts import CrackerS1
from cracknuts.cracker.protocol import Command


class CrushCommand(Command):
    QSPI_SET_ENABLE = 0x0340
    QSPI_RESET = 0x0341
    QSPI_SET_POST_DELAY = 0x0342
    QSPI_SET_FIX_DATA = 0x0343
    QSPI_SET_FAB_DATA = 0x0344
    QSPI_CLEAR_BUFFER = 0x0345
    QSPI_ACTION = 0x0346


class Crush(CrackerS1):
    def qspi_set_enable(self, enable: bool):
        payload = struct.pack(">B", enable)
        self._logger.debug(f"qspi_set_enable payload: {payload.hex()}")
        status, _ = self.send_with_command(CrushCommand.QSPI_SET_ENABLE, payload=payload)
        return status, None

    def qspi_reset(self):
        self._logger.debug(f"qspi_reset payload: {None}")
        status, _ = self.send_with_command(CrushCommand.QSPI_RESET)

    def qspi_set_post_delay(self, delay: int):
        payload = struct.pack(">H", delay)
        self._logger.debug(f"qspi_set_post_delay payload: {payload.hex()}")
        status, _ = self.send_with_command(CrushCommand.QSPI_SET_POST_DELAY, payload=payload)

    def qspi_set_fix_data(self, fix_data: bytes | str):
        if isinstance(fix_data, str):
            fix_data = bytes.fromhex(fix_data)
        self._logger.debug(f"qspi_set_fix_data payload: {fix_data.hex()}")
        status, _ = self.send_with_command(CrushCommand.QSPI_SET_FIX_DATA, payload=fix_data)

    def qspi_set_fab_data(self, fab_data: bytes | str):
        if isinstance(fab_data, str):
            fab_data = bytes.fromhex(fab_data)
        self._logger.debug(f"qspi_set_fab_data payload: {fab_data.hex()}")
        status, _ = self.send_with_command(CrushCommand.QSPI_SET_FAB_DATA, payload=fab_data)

    def qspi_clear_buffer(self):
        self._logger.debug(f"qspi_clear_buffer payload: {None}")
        status, _ = self.send_with_command(CrushCommand.QSPI_CLEAR_BUFFER)

    def qspi_action(self):
        self._logger.debug(f"qspi_action payload: {None}")
        status, _ = self.send_with_command(CrushCommand.QSPI_ACTION)
