import logging
import struct
import threading
import time

import pytest

import cracknuts.mock as mock
from cracknuts.cracker.cracker_s1 import CrackerS1
from cracknuts.cracker.protocol import Command
from cracknuts.logger import set_level


@pytest.fixture(scope='module')
def mock_cracker():
    def start_mock_cracker():
        mock.start(logging_level=logging.WARNING)

    mock_thread = threading.Thread(target=start_mock_cracker)
    mock_thread.daemon = True
    mock_thread.start()
    time.sleep(0.5)
    yield


@pytest.fixture(scope='module')
def cracker_s1(mock_cracker):
    device = CrackerS1(address=('localhost', 9761))
    # set_level(logging.INFO, device)
    device.connect(update_bin=False)
    yield device
    device.disconnect()


def get_result_by_command(device, command):
    _, r = device.send_with_command(0xFFFF, payload=struct.pack('>I', command))
    return r


def test_nut_voltage(cracker_s1):
    s, _ = cracker_s1.nut_voltage("3.3")
    assert s == 0 and cracker_s1.get_current_config().nut_voltage == 3.3
    assert get_result_by_command(cracker_s1, Command.NUT_VOLTAGE) == struct.pack('>I', 3300)

    s, _ = cracker_s1.nut_voltage("3.4v")
    assert s == 0 and cracker_s1.get_current_config().nut_voltage == 3.4
    assert get_result_by_command(cracker_s1, Command.NUT_VOLTAGE) == struct.pack('>I', 3400)

    s, _ = cracker_s1.nut_voltage("3500mV")
    assert s == 0 and cracker_s1.get_current_config().nut_voltage == 3.5
    assert get_result_by_command(cracker_s1, Command.NUT_VOLTAGE) == struct.pack('>I', 3500)

    s, _ = cracker_s1.nut_voltage("3.6")
    assert s == 0 and cracker_s1.get_current_config().nut_voltage == 3.6
    assert get_result_by_command(cracker_s1, Command.NUT_VOLTAGE) == struct.pack('>I', 3600)

    s, _ = cracker_s1.nut_voltage(3.6)
    assert s == 0 and cracker_s1.get_current_config().nut_voltage == 3.6
    assert get_result_by_command(cracker_s1, Command.NUT_VOLTAGE) == struct.pack('>I', 3600)

    s, _ = cracker_s1.nut_voltage("3.7K")
    assert s == -1


def test_osc_sample_clock(cracker_s1):
    clock_values = (65000, 48000, 24000, 12000, 8000, 4000)

    for clock in clock_values:
        s, _ = cracker_s1.osc_sample_clock(str(clock))
        assert s == 0 and cracker_s1.get_current_config().osc_sample_clock == clock
        assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_RATE) == struct.pack('>I', clock)

        s, _ = cracker_s1.osc_sample_clock(clock)
        assert s == 0 and cracker_s1.get_current_config().osc_sample_clock == clock
        assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_RATE) == struct.pack('>I', clock)

    clock_str_values = ("65M", "48M", "24M", "12M", "8M", "4M")
    for i, clock in enumerate(clock_str_values):
        s, _ = cracker_s1.osc_sample_clock(clock)
        assert s == 0 and cracker_s1.get_current_config().osc_sample_clock == clock_values[i]
        assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_RATE) == struct.pack('>I', clock_values[i])

    s, _ = cracker_s1.osc_sample_clock("69M")
    assert s == -1


def test_osc_sample_length(cracker_s1):
    s, _ = cracker_s1.osc_sample_length(1024)
    assert s == 0 and cracker_s1.get_current_config().osc_sample_length == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_LENGTH) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_length("1k")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_length == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_LENGTH) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_length("1K")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_length == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_LENGTH) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_length("1m")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_length == 1024 * 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_LENGTH) == struct.pack('>I', 1024 * 1024)

    s, _ = cracker_s1.osc_sample_length("1M")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_length == 1024 * 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_LENGTH) == struct.pack('>I', 1024 * 1024)


def test_osc_sample_delay(cracker_s1):
    s, _ = cracker_s1.osc_sample_delay(1024)
    assert s == 0 and cracker_s1.get_current_config().osc_sample_delay == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_DELAY) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_delay("1k")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_delay == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_DELAY) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_delay("1K")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_delay == 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_DELAY) == struct.pack('>I', 1024)

    s, _ = cracker_s1.osc_sample_delay("1m")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_delay == 1024 * 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_DELAY) == struct.pack('>I', 1024 * 1024)

    s, _ = cracker_s1.osc_sample_delay("1M")
    assert s == 0 and cracker_s1.get_current_config().osc_sample_delay == 1024 * 1024
    assert get_result_by_command(cracker_s1, Command.OSC_SAMPLE_DELAY) == struct.pack('>I', 1024 * 1024)


def test_osc_trigger_mode(cracker_s1):
    modes1 = ("EDGE", "PATTERN")
    modes2 = ("E", "P")
    for modes in modes1, modes2:
        for mode in modes:
            s, _ = cracker_s1.osc_trigger_mode(mode)
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_mode == modes.index(mode)
            assert get_result_by_command(cracker_s1, Command.OSC_TRIGGER_MODE) == struct.pack('>B', modes.index(mode))

            s, _ = cracker_s1.osc_trigger_mode(modes.index(mode))
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_mode == modes.index(mode)
            assert get_result_by_command(cracker_s1, Command.OSC_TRIGGER_MODE) == struct.pack('>B', modes.index(mode))

    s, _ = cracker_s1.osc_trigger_mode("x")
    assert s == -1

    s, _ = cracker_s1.osc_trigger_mode(5)
    assert s == -1


def test_osc_trigger_source(cracker_s1):
    sources1 = ('N', 'A', 'B', 'P')
    sources2 = ('NUT', 'CHA', 'CHB', "PROTOCOL")
    for sources in sources1, sources2:
        for source in sources:
            s, _ = cracker_s1.osc_trigger_source(source)
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_source == sources.index(source)
            assert get_result_by_command(cracker_s1, Command.OSC_ANALOG_TRIGGER_SOURCE) == struct.pack('>B',
                                                                                                       sources.index(
                                                                                                           source))

            s, _ = cracker_s1.osc_trigger_source(sources.index(source))
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_source == sources.index(source)
            assert get_result_by_command(cracker_s1, Command.OSC_ANALOG_TRIGGER_SOURCE) == struct.pack('>B',
                                                                                                       sources.index(
                                                                                                           source))

    s, _ = cracker_s1.osc_trigger_source("x")
    assert s == -1

    s, _ = cracker_s1.osc_trigger_source(5)
    assert s == -1


def test_osc_trigger_edge(cracker_s1):
    edges1 = ('UP', 'DOWN', 'EITHER')
    edges2 = ('U', 'D', 'E')
    for edges in edges1, edges2, tuple(e.lower() for e in edges1), tuple(e.lower() for e in edges2):
        for edge in edges:
            s, _ = cracker_s1.osc_trigger_edge(edge)
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_edge == edges.index(edge)
            assert get_result_by_command(cracker_s1, Command.OSC_TRIGGER_EDGE) == struct.pack('>B', edges.index(edge))

            s, _ = cracker_s1.osc_trigger_edge(edges.index(edge))
            assert s == 0 and cracker_s1.get_current_config().osc_trigger_edge == edges.index(edge)
            assert get_result_by_command(cracker_s1, Command.OSC_TRIGGER_EDGE) == struct.pack('>B', edges.index(edge))

    s, _ = cracker_s1.osc_trigger_edge("x")
    assert s == -1

    s, _ = cracker_s1.osc_trigger_edge(5)
    assert s == -1


def test_osc_analog_gain(cracker_s1):
    channels =  ('A', 'B')
    for i, channel in enumerate(channels):
        s, _ = cracker_s1.osc_analog_gain(channel, 10)
        assert s == 0 and cracker_s1.get_current_config().osc_analog_gain[channels.index(channel)] == 10
        assert get_result_by_command(cracker_s1, Command.OSC_ANALOG_GAIN) == struct.pack('>B', channels.index(channel)) + struct.pack('>B', 10)

        s, _ = cracker_s1.osc_analog_gain(i, 10)
        assert s == 0 and cracker_s1.get_current_config().osc_analog_gain[i] == 10
        assert get_result_by_command(cracker_s1, Command.OSC_ANALOG_GAIN) == struct.pack('>B', i) + struct.pack('>B', 10)

    s, _ = cracker_s1.osc_analog_gain("x", 10)
    assert s == -1

    s, _ = cracker_s1.osc_analog_gain(2, 10)
    assert s == -1


def test_osc_analog_enable_disable(cracker_s1):
    channels = ('A', 'B')
    for i, channel in enumerate(channels):
        m = 1 << i

        s, _ = cracker_s1.osc_analog_enable(channel)
        assert s == 0 and cracker_s1.get_current_config().osc_analog_channel_enable[i] == True

        assert struct.unpack(">B", get_result_by_command(cracker_s1, Command.OSC_ANALOG_CHANNEL_ENABLE))[0] & m == m

        s, _ = cracker_s1.osc_analog_disable(channel)
        assert s == 0 and cracker_s1.get_current_config().osc_analog_channel_enable[i] == False
        assert struct.unpack(">B", get_result_by_command(cracker_s1, Command.OSC_ANALOG_CHANNEL_ENABLE))[0] & m == 0