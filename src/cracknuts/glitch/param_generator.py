import abc
import itertools
from enum import Enum
import random


class GlitchGenerateParam:
    class Mode(Enum):
        INCREASE = 0
        DECREASE = 1
        RANDOM = 2
        FIXED = 3

    def __init__(self, mode, start, end, step, count):
        self.mode = mode
        self.start = start
        self.end = end
        self.step = step
        self.count = count

    def __str__(self):
        return str(self.__dict__)


class AbstractGlitchParamGenerator(abc.ABC):
    def __init__(self):
        self._generate_params = self._build()
        self._current_index = 0

    def _build(self) -> list[GlitchGenerateParam]: ...

    @staticmethod
    def _do_build(param: GlitchGenerateParam):
        if param.mode == GlitchGenerateParam.Mode.FIXED:
            return [param.start for _ in range(param.count)]
        if param.mode == GlitchGenerateParam.Mode.INCREASE:
            return list(AbstractGlitchParamGenerator._frange(param.start, param.end, param.step)) * param.count
        if param.mode == GlitchGenerateParam.Mode.DECREASE:
            return list(AbstractGlitchParamGenerator._frange(param.end, param.start, -param.step)) * param.count
        if param.mode == GlitchGenerateParam.Mode.RANDOM:
            return [random.randint(param.start, param.end) for _ in range(param.count)]
        return []

    @staticmethod
    def _frange(start, stop, step):
        x = start
        while x <= stop:
            yield round(x, 10)
            x += step

    def total(self):
        return len(self._generate_params)

    def next(self):
        param = self._generate_params[self._current_index]
        self._current_index += 1
        if self._current_index >= len(self._generate_params):
            self._current_index = 0
        return param


class VCCGlitchParam:
    def __init__(self, normal: int, wait: int, glitch: int, count: int, repeat: int, interval: int):
        self.normal = normal
        self.wait = wait
        self.glitch = glitch
        self.count = count
        self.repeat = repeat
        self.interval = interval


class VCCGlitchParamGenerator(AbstractGlitchParamGenerator):
    def __init__(
        self,
        normal: GlitchGenerateParam,
        wait: GlitchGenerateParam,
        glitch: GlitchGenerateParam,
        count: GlitchGenerateParam,
        repeat: GlitchGenerateParam,
        interval: GlitchGenerateParam,
    ):
        self.normal = normal
        self.wait = wait
        self.glitch = glitch
        self.count = count
        self.repeat = repeat
        self.interval = interval
        super().__init__()

    def _build(self):
        normal_list = []
        wait_list = []
        glitch_list = []
        count_list = []
        repeat_list = []
        interval_list = []
        if self.normal is not None:
            normal_list = self._do_build(self.normal)
        if self.wait is not None:
            wait_list = self._do_build(self.wait)
        if self.glitch is not None:
            glitch_list = self._do_build(self.glitch)
        if self.count is not None:
            count_list = self._do_build(self.count)
        if self.repeat is not None:
            repeat_list = self._do_build(self.repeat)
        if self.interval is not None:
            interval_list = self._do_build(self.interval)

        return [
            VCCGlitchParam(*combo)
            for combo in itertools.product(
                normal_list,
                wait_list,
                glitch_list,
                count_list,
                repeat_list,
                interval_list,
            )
        ]

    def __str__(self):
        return str(self.__dict__)


class GNDGlitchParamGenerator(VCCGlitchParamGenerator): ...
