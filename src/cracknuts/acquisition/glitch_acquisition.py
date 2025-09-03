import abc
import datetime
import enum
import sqlite3
import typing

from cracknuts import Acquisition, CrackerBasic, AcquisitionBuilder, CrackerG1
from cracknuts.glitch.param_generator import AbstractGlitchParamGenerator, VCCGlitchParam, VCCGlitchParamGenerator


class GlitchTestResult(abc.ABC):
    def __init__(self, path: str, create=True):
        self._path = path
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()
        if create:
            self._init_table()

    def _init_table(self): ...

    def add(self, param, data: "GlitchDoData"): ...

    def close(self):
        self._cursor.close()
        self._conn.close()


class VCCGlitchTestResult(GlitchTestResult):
    def _init_table(self):
        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS glitch_result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normal INTEGER,
            wait INTEGER,
            glitch INTEGER,
            `count` INTEGER,
            repeat INTEGER,
            `interval` INTEGER,
            plaintext BLOB,
            ciphertext BLOB,
            `key` BLOB,
            extended BLOB,
            status INTEGER
        )
        """)
        self._conn.commit()

    def add(self, param: VCCGlitchParam, data: "GlitchDoData"):
        self._cursor.execute(
            """
                INSERT INTO glitch_result (
                    normal, wait, glitch, count, repeat, interval, plaintext, ciphertext, key, extended, glitch_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
            (
                param.normal,
                param.wait,
                param.glitch,
                param.count,
                param.repeat,
                param.interval,
                data.plaintext,
                data.ciphertext,
                data.key,
                data.extended,
                data.glitch_status.value,
            ),
        )
        self._conn.commit()


class GlitchAcquisition(Acquisition):
    def __init__(
        self,
        cracker: CrackerBasic,
        trace_count: int = 1000,
        sample_length: int = -1,
        sample_offset: int = 0,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float = 0.05,
        trigger_judge_timeout: float = 1.0,
        do_error_handler_strategy: int = Acquisition.DO_ERROR_HANDLER_STRATEGY_EXIT,
        do_error_max_count: int = -1,
        file_format: str = "zarr",
        file_path: str = "auto",
        trace_fetch_interval: float = 0,
    ):
        super().__init__(
            cracker,
            trace_count,
            sample_length,
            sample_offset,
            data_plaintext_length,
            data_ciphertext_length,
            data_key_length,
            data_extended_length,
            trigger_judge_wait_time,
            trigger_judge_timeout,
            do_error_handler_strategy,
            do_error_max_count,
            file_format,
            file_path,
            trace_fetch_interval,
        )
        self._glitch_result = None
        self._glitch_param_generator: AbstractGlitchParamGenerator | None = None
        self._current_glitch_param = None

    def pre_init(self):
        # 初始化存储数据
        self._glitch_result = GlitchTestResult(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), create=True)

    def init(self): ...

    def do(self) -> "GlitchDoData": ...

    def pre_do(self):
        # 设置当前的glitch参数
        if isinstance(self._glitch_param_generator, VCCGlitchParamGenerator):
            glitch_param = self._glitch_param_generator.next()
            cracker_g1: CrackerG1 = typing.cast(self.cracker, CrackerG1)
            cracker_g1.glitch_vcc_config(
                wait=glitch_param.wait,
                level=glitch_param.glitch,
                count=glitch_param.count,
                delay=glitch_param.interval,
                repeat=glitch_param.repeat,
            )
            self._current_glitch_param = glitch_param
        # OTHER GLITCH PARAM GENERATOR

    def _post_do(self, data):
        self._glitch_result.add(self._current_glitch_param, data)

    def _pre_finish(self):
        self._glitch_result.close()

    def set_glitch_params(self, param_generator: AbstractGlitchParamGenerator):
        self._glitch_param_generator = param_generator
        self.trace_count = self._glitch_param_generator.total()

    def do_glitch_test(
        self,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        data_plaintext_length: int | None = None,
        data_ciphertext_length: int | None = None,
        data_key_length: int | None = None,
        data_extended_length: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        file_format: str | None = "zarr",
        file_path: str | None = "auto",
        trace_fetch_interval: float = 0.1,
    ):
        self._run(
            test=False,
            persistent=False,
            count=self.trace_count,
            sample_length=sample_length,
            sample_offset=sample_offset,
            data_plaintext_length=data_plaintext_length,
            data_ciphertext_length=data_ciphertext_length,
            data_key_length=data_key_length,
            data_extended_length=data_extended_length,
            trigger_judge_wait_time=trigger_judge_wait_time,
            trigger_judge_timeout=trigger_judge_timeout,
            do_error_max_count=do_error_max_count,
            do_error_handler_strategy=do_error_handler_strategy,
            file_format=file_format,
            file_path=file_path,
            trace_fetch_interval=trace_fetch_interval,
        )


class GlitchDoStatus(enum.Enum):
    GLITCHED = 0
    NOT_GLITCHED = 1
    NO_RETURN = 2
    ERROR = 3


class GlitchDoData:
    def __init__(
        self,
        plaintext: bytes | None = None,
        ciphertext: bytes | None = None,
        key: bytes | None = None,
        extended: bytes | None = None,
        glitch_status: GlitchDoStatus = GlitchDoStatus.NOT_GLITCHED,
    ):
        self.plaintext = plaintext
        self.ciphertext = ciphertext
        self.key = key
        self.extended = extended
        self.glitch_status = glitch_status


class GlitchAcquisitionBuilder(AcquisitionBuilder):
    def build(self, **kwargs):
        """
        Build the acquisition object.

        :param kwargs: other keyword arguments of Acquisition.
        :type kwargs: dict
        :return Acquisition
        """
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

            def finish(self):
                builder_self._finish_function(self.cracker)

        return AnonymousAcquisition(self._cracker, **kwargs)
