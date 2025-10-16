import abc
import enum
import sqlite3
import typing
from abc import ABC

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

    def open(self):
        self._conn = sqlite3.connect(self._path)
        self._cursor = self._conn.cursor()


class VCCGlitchTestResult(GlitchTestResult):
    def _init_table(self):
        self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS glitch_result (
            `no` INTEGER PRIMARY KEY,
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
        if data.glitch_status is None:
            data.glitch_status = GlitchDoStatus.ERROR
        data.key = data.key.hex() if data.key is not None else ""
        data.ciphertext = data.ciphertext.hex() if data.ciphertext is not None else ""
        data.plaintext = data.plaintext.hex() if data.plaintext is not None else ""
        data.extended = data.extended.hex() if data.extended is not None else ""
        self._cursor.execute(
            """
                INSERT INTO glitch_result (
                    normal, wait, glitch, count, repeat, interval, plaintext, ciphertext, key, extended, status
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


class GlitchAcquisition(Acquisition, ABC):
    def __init__(
        self,
        cracker: CrackerBasic,
        trace_count: int = 1000,
        shadow_trace_count: int = 1000,
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
        self._shadow_trace_count = shadow_trace_count
        self._cracker_g1 = typing.cast(CrackerG1, self.cracker)
        self._glitch_result = None
        self._glitch_param_generator: AbstractGlitchParamGenerator | None = None
        self._current_glitch_param = None
        self._is_in_glitch_mode = False
        self._glitch_test_params = None

    @property
    def shadow_trace_count(self):
        return self._shadow_trace_count

    @shadow_trace_count.setter
    def shadow_trace_count(self, value: int):
        self._shadow_trace_count = value
        for listener in self._on_config_changed_listener:
            listener("shadow_trace_count", value)

    def pre_init(self):
        if not self._is_in_glitch_mode:
            return
        if isinstance(self._glitch_param_generator, VCCGlitchParamGenerator):
            self._glitch_result = VCCGlitchTestResult(f"dataset/{self._current_timestamp}_vcc.sqlite3", create=True)
        else:
            # todo other glitch test result.
            ...

    def do(self, count: int) -> "GlitchDoData": ...

    def pre_do(self):
        if not self._is_in_glitch_mode:
            return
        # 设置当前的glitch参数
        if isinstance(self._glitch_param_generator, VCCGlitchParamGenerator):
            glitch_param = self._glitch_param_generator.next()
            cracker_g1: CrackerG1 = typing.cast(CrackerG1, self.cracker)
            cracker_g1.glitch_vcc_config(
                wait=glitch_param.wait,
                level=glitch_param.glitch,
                count=glitch_param.count,
                delay=glitch_param.interval,
                repeat=glitch_param.repeat,
            )
            self._current_glitch_param = glitch_param
        # OTHER GLITCH PARAM GENERATOR
        self.cracker.osc_single()

    def _post_do(self, data):
        if not self._is_in_glitch_mode:
            return
        self._glitch_result.add(self._current_glitch_param, GlitchDoData(**data))

    def _pre_finish(self):
        if not self._is_in_glitch_mode:
            return
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
        self._is_in_glitch_mode = False
        self.test(
            count=count,
            sample_length=sample_length,
            sample_offset=sample_offset,
            trigger_judge_wait_time=trigger_judge_wait_time,
            trigger_judge_timeout=trigger_judge_timeout,
            do_error_max_count=do_error_max_count,
            do_error_handler_strategy=do_error_handler_strategy,
            trace_fetch_interval=trace_fetch_interval,
        )

    # def glitch_test(
    #     self,
    #     sample_length: int | None = None,
    #     sample_offset: int | None = None,
    #     trigger_judge_wait_time: float | None = None,
    #     trigger_judge_timeout: float | None = None,
    #     do_error_max_count: int | None = None,
    #     do_error_handler_strategy: int | None = None,
    #     trace_fetch_interval: float = 0.1,
    # ):
    #     glitch_params = self._build_glitch_param_generator(self._glitch_test_params)
    #     self._logger.warning(f"glitch_params: {glitch_params}")
    #     self.set_glitch_params(glitch_params)
    #     self._logger.warning(f"count is {self.trace_count}")
    #
    #     test_mode = self._glitch_param_generator.total() == 1
    #     count = -1 if test_mode else self._glitch_param_generator.total()
    #
    #     self._is_in_glitch_mode = True
    #     self._run(
    #         test=test_mode,
    #         persistent=False,
    #         count=count,
    #         sample_length=sample_length,
    #         sample_offset=sample_offset,
    #         trigger_judge_wait_time=trigger_judge_wait_time,
    #         trigger_judge_timeout=trigger_judge_timeout,
    #         do_error_max_count=do_error_max_count,
    #         do_error_handler_strategy=do_error_handler_strategy,
    #         trace_fetch_interval=trace_fetch_interval,
    #     )

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
        self._is_in_glitch_mode = False
        self.run(
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
        count: int | None = None,
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
        glitch_params = self._build_glitch_param_generator(self._glitch_test_params)
        self.set_glitch_params(glitch_params)

        if count is None:
            count = self.shadow_trace_count
        count = count * self._glitch_param_generator.total()
        self._is_in_glitch_mode = True
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
            is_glitch=True,
        )

    @staticmethod
    def _build_glitch_param_generator(glitch_params) -> None | VCCGlitchParamGenerator | GNDGlitchParamGenerator:
        if glitch_params["type"] == "vcc":
            normal, wait, glitch, count, repeat, interval = None, None, None, None, None, None
            for param in glitch_params["data"]:
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

    def set_glitch_test_params(self, param):
        self._glitch_test_params = param

    def get_glitch_test_params(self):
        return self._glitch_test_params


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
        glitch_status: GlitchDoStatus | int = GlitchDoStatus.NOT_GLITCHED,
    ):
        self.plaintext = plaintext
        self.ciphertext = ciphertext
        self.key = key
        self.extended = extended
        if isinstance(glitch_status, int):
            glitch_status = GlitchDoStatus(glitch_status)
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
                builder_self._init_function()

            def do(self, count: int):
                return builder_self._do_function(count)

            def finish(self):
                builder_self._finish_function()

        return AnonymousAcquisition(self._cracker, **kwargs)
