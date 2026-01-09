import ctypes
import numpy as np
from picosdk.psospa import psospa as ps
from picosdk.PicoDeviceEnums import picoEnum as enums
from picosdk.functions import adc2mVV2, assert_pico_ok


class PicoScopeAverager:
    def __init__(self, resolution_bits=8, voltage_range_v=10, sample_count=10000):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.sample_count = sample_count
        self.voltage_range_v = voltage_range_v
        self.rangeMin = -int(voltage_range_v * 1e9)  # in nV
        self.rangeMax =  int(voltage_range_v * 1e9)
        self.buffer = (ctypes.c_int16 * sample_count)()
        self.bufferMin = (ctypes.c_int16 * sample_count)()
        self.resolution = enums.PICO_DEVICE_RESOLUTION[f"PICO_DR_{resolution_bits}BIT"]

        self._open_device()
        self._configure_channel()
        self._get_adc_limits()
        self._allocate_buffer()

    def _open_device(self):
        self.status["openUnit"] = ps.psospaOpenUnit(ctypes.byref(self.chandle), None, self.resolution, None)
        assert_pico_ok(self.status["openUnit"])

    def _configure_channel(self):
        channelA = enums.PICO_CHANNEL["PICO_CHANNEL_A"]
        coupling = enums.PICO_COUPLING["PICO_DC"]
        rangeType = 0
        analogueOffset = 0
        bandwidth = enums.PICO_BANDWIDTH_LIMITER["PICO_BW_FULL"]

        self.status["setChannelA"] = ps.psospaSetChannelOn(
            self.chandle, channelA, coupling,
            self.rangeMin, self.rangeMax,
            rangeType, analogueOffset, bandwidth)
        assert_pico_ok(self.status["setChannelA"])

        # 关闭其他通道
        for ch in ['B', 'C', 'D']:
            channelX = enums.PICO_CHANNEL[f'PICO_CHANNEL_{ch}']
            self.status[f"setChannel{ch}"] = ps.psospaSetChannelOff(self.chandle, channelX)
            assert_pico_ok(self.status[f"setChannel{ch}"])

    def _get_adc_limits(self):
        self.minADC = ctypes.c_int16()
        self.maxADC = ctypes.c_int16()
        self.status["getAdcLimits"] = ps.psospaGetAdcLimits(
            self.chandle, self.resolution,
            ctypes.byref(self.minADC), ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["getAdcLimits"])

    def _allocate_buffer(self):
        # 获取最小可用 timebase
        flags = enums.PICO_CHANNEL_FLAGS["PICO_CHANNEL_A_FLAGS"]
        self.timebase = ctypes.c_uint32(0)
        self.timeInterval = ctypes.c_double(0)
        self.status["getTimebase"] = ps.psospaGetMinimumTimebaseStateless(
            self.chandle, flags, ctypes.byref(self.timebase),
            ctypes.byref(self.timeInterval), self.resolution)
        assert_pico_ok(self.status["getTimebase"])

        # 设置 memory segment
        self.status["memorySegments"] = ps.psospaMemorySegments(self.chandle, 1, ctypes.byref(ctypes.c_uint64(1)))
        assert_pico_ok(self.status["memorySegments"])
        self.status["setNoOfCaptures"] = ps.psospaSetNoOfCaptures(self.chandle, 1)
        assert_pico_ok(self.status["setNoOfCaptures"])

        # 配置 buffer
        dataType = enums.PICO_DATA_TYPE["PICO_INT16_T"]
        mode = enums.PICO_RATIO_MODE["PICO_RATIO_MODE_RAW"]
        action = enums.PICO_ACTION["PICO_CLEAR_ALL"] | enums.PICO_ACTION["PICO_ADD"]

        self.status["setDataBuffers"] = ps.psospaSetDataBuffers(
            self.chandle, enums.PICO_CHANNEL["PICO_CHANNEL_A"],
            ctypes.byref(self.buffer), ctypes.byref(self.bufferMin),
            self.sample_count, dataType, 0, mode, action)
        assert_pico_ok(self.status["setDataBuffers"])

    def read_avg_voltage_mv(self):
        # 运行采集
        timeIndisposedMs = ctypes.c_double(0)
        self.status["runBlock"] = ps.psospaRunBlock(
            self.chandle, 0, self.sample_count, self.timebase,
            ctypes.byref(timeIndisposedMs), 0, None, None)
        assert_pico_ok(self.status["runBlock"])

        # 等待就绪
        ready = ctypes.c_int16(0)
        while not ready.value:
            self.status["isReady"] = ps.psospaIsReady(self.chandle, ctypes.byref(ready))

        # 获取数据
        noOfSamples = ctypes.c_uint64(self.sample_count)
        overflow = (ctypes.c_int16 * 1)()
        mode = enums.PICO_RATIO_MODE["PICO_RATIO_MODE_RAW"]

        self.status["getValues"] = ps.psospaGetValuesBulk(
            self.chandle, 0, ctypes.byref(noOfSamples),
            0, 0, 1, mode, ctypes.byref(overflow))
        assert_pico_ok(self.status["getValues"])

        voltages = adc2mVV2(self.buffer, self.rangeMax, self.maxADC)
        avg_mv = np.mean(voltages)
        return avg_mv

    def close(self):
        self.status["closeunit"] = ps.psospaCloseUnit(self.chandle)
        assert_pico_ok(self.status["closeunit"])


if __name__ == "__main__":
    scope = PicoScopeAverager(sample_count=10000, voltage_range_v=10)

    for i in range(5):
        avg = scope.read_avg_voltage_mv()
        print(f"[{i}] 通道 A 平均电压: {avg:.2f} mV")

    scope.close()
