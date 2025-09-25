import abc
import datetime
import enum
import sqlite3
import typing

from cracknuts import Acquisition, CrackerBasic, AcquisitionBuilder, CrackerG1
from cracknuts.glitch.param_generator import (
    AbstractGlitchParamGenerator,
    VCCGlitchParam,
    VCCGlitchParamGenerator,
    GlitchGenerateParam,
    GNDGlitchParamGenerator,
)


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
        self._cracker_g1 = typing.cast(CrackerG1, self.cracker)
        self._glitch_result = None
        self._glitch_param_generator: AbstractGlitchParamGenerator | None = None
        self._current_glitch_param = None

    def pre_init(self):
        self._glitch_result = GlitchTestResult(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), create=True)

    def init(self): ...

    def do(self, count: int) -> "GlitchDoData": ...

    def pre_do(self):
        # 设置当前的glitch参数
        if isinstance(self._glitch_param_generator, VCCGlitchParamGenerator):
            glitch_param = self._glitch_param_generator.next()
            cracker_g1: CrackerG1 = typing.cast(self.cracker, CrackerG1)
            print(f"type of cracker_g1: {type(cracker_g1)}")
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
        # self.trace_count = self._glitch_param_generator.total()

    def test(
        self,
        count=-1,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        trace_fetch_interval: float = 2.0,
    ):
        self.glitch_test(
            sample_length=sample_length,
            sample_offset=sample_offset,
            trigger_judge_wait_time=trigger_judge_wait_time,
            trigger_judge_timeout=trigger_judge_timeout,
            do_error_max_count=do_error_max_count,
            do_error_handler_strategy=do_error_handler_strategy,
            trace_fetch_interval=trace_fetch_interval,
        )

    def glitch_test(
        self,
        sample_length: int | None = None,
        sample_offset: int | None = None,
        trigger_judge_wait_time: float | None = None,
        trigger_judge_timeout: float | None = None,
        do_error_max_count: int | None = None,
        do_error_handler_strategy: int | None = None,
        trace_fetch_interval: float = 0.1,
    ):
        glitch_params = self._build_glitch_param_generator(self._cracker_g1.get_glitch_test_params())
        self._logger.warning(f"glitch_params: {glitch_params}")
        self.set_glitch_params(glitch_params)
        self._logger.warning(f"count is {self.trace_count}")

        test_mode = self._glitch_param_generator.total() == 1
        count = -1 if test_mode else self._glitch_param_generator.total()

        self._run(
            test=test_mode,
            persistent=False,
            count=count,
            sample_length=sample_length,
            sample_offset=sample_offset,
            trigger_judge_wait_time=trigger_judge_wait_time,
            trigger_judge_timeout=trigger_judge_timeout,
            do_error_max_count=do_error_max_count,
            do_error_handler_strategy=do_error_handler_strategy,
            trace_fetch_interval=trace_fetch_interval,
        )

    def run(
        self,
        count: int = 1,
        sample_length: int = 1024,
        sample_offset: int = 0,
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
    ):
        self.glitch_run(
            count=count,
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
        )

    def glitch_run(
        self,
        count: int = 1,
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
        glitch_params = self._build_glitch_param_generator(self._cracker_g1.get_glitch_test_params())
        self._logger.warning(f"glitch_params: {glitch_params}")
        self.set_glitch_params(glitch_params)
        self._logger.warning(f"count is {self.trace_count}")

        count = count * self._glitch_param_generator.total()

        self._run(
            test=False,
            persistent=True,
            count=count,
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

    @staticmethod
    def _build_glitch_param_generator(glitch_params) -> None | VCCGlitchParamGenerator | GNDGlitchParamGenerator:
        if glitch_params["type"] == "vcc":
            normal, wait, glitch, count, repeat, interval = None, None, None, None, None, None
            for param in glitch_params["params"]:
                if param["prop"] == "normal":
                    g_param = param["param"]
                    normal = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "wait":
                    g_param = param["param"]
                    wait = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "glitch":
                    g_param = param["param"]
                    glitch = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "count":
                    g_param = param["param"]
                    count = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "repeat":
                    g_param = param["param"]
                    repeat = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "interval":
                    g_param = param["param"]
                    interval = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
            return VCCGlitchParamGenerator(normal, wait, glitch, count, repeat, interval)
        elif glitch_params["type"] == "gnd":
            normal, wait, glitch, count, repeat, interval = None, None, None, None, None, None
            for param in glitch_params["params"]:
                if param["prop"] == "normal":
                    g_param = param["param"]
                    normal = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "wait":
                    g_param = param["param"]
                    wait = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "glitch":
                    g_param = param["param"]
                    glitch = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "count":
                    g_param = param["param"]
                    count = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "repeat":
                    g_param = param["param"]
                    repeat = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
                elif param["prop"] == "interval":
                    g_param = param["param"]
                    interval = GlitchGenerateParam(
                        start=g_param["start"],
                        end=g_param["end"],
                        count=g_param["count"],
                        step=g_param["step"],
                        mode=GlitchGenerateParam.Mode(g_param["mode"]),
                    )
            return GNDGlitchParamGenerator(normal, wait, glitch, count, repeat, interval)
        elif glitch_params["type"] == "clock":
            ...
        else:
            raise ValueError("Unknown glitch param type")

    def glitch_test_sync(
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
        self._do_run(
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

        class AnonymousAcquisition(GlitchAcquisition):
            def __init__(self, *ana_args, **ana_kwargs):
                super().__init__(*ana_args, **ana_kwargs)

            def init(self):
                builder_self._init_function(self.cracker)

            def do(self, count: int):
                return builder_self._do_function(self.cracker)

            def finish(self):
                builder_self._finish_function(self.cracker)

        return AnonymousAcquisition(self._cracker, **kwargs)
