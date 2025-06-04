import os
import time
from threading import Thread

import pytest
import serial
from serial.tools import list_ports

from cracknuts import CrackerS1
from cracknuts.cracker import serial as cn_serial

class DynamicSerialServer(Thread):
    def __init__(self, port=None, baudrate=115200, bytesize=8, stopbits=1, parity='N', response_rules=None, response_delay=0.0):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.parity = parity
        self.response_rules = response_rules or {}
        self.response_delay = response_delay
        self.ser = None
        self._running = False
        self.rec_cache = b''

    def run(self):
        if not self.port:
            self.port = self._find_serial_port(exclude_ports=['COM1'])
            if not self.port:
                print("[ERROR] 未发现可用串口")
                return
            # print(f"[INFO] 自动发现串口：{self.port}")
        self._running = True
        ser = None
        try:
            ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                stopbits=self.stopbits,
                parity=self.parity,
                timeout=1
            )

            while self._running:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if not data:
                        continue

                    print(f"[RECV] {data.hex(' ')}")
                    self.rec_cache += data
                    print(f"[RECV CACHE] {self.rec_cache.hex(' ')}")

                    if self.response_rules:
                        response = self.response_rules.get(data)
                    else:
                        print("[INFO] 未设置响应规则，使用默认回声响应，清空已处理的数据")
                        response = data
                        self.rec_cache = self.rec_cache[:-len(data)]  # 清除已处理的数据

                    if response:
                        if self.response_delay > 0:
                            time.sleep(self.response_delay)
                        ser.write(response)
                        # print(f"[SEND] {response.hex(' ')}")

        except serial.SerialException as e:
            print(f"[ERROR] 串口错误：{e}")
        except KeyboardInterrupt:
            print("[INFO] 中断退出")
        finally:
            # print(f"[INFO] 关闭串口服务：{self.port}")
            if ser and ser.is_open:
                ser.close()

    def stop(self):
        self._running = False

    def get_received_data(self, expected_len=None):
        """
        获取接收到的数据缓存，并清空缓存
        """
        if expected_len:
            timeout = 10  # 最长等待时间为10秒
            start_time = time.time()
            while len(self.rec_cache) < expected_len and (time.time() - start_time) < timeout:
                time.sleep(0.1)  # 等待数据接收完成
        data = self.rec_cache
        self.rec_cache = b''
        return data

    def send_data(self, data):
        """
        发送数据到串口
        """
        timeout = 10  # 最长等待时间为10秒
        start_time = time.time()
        while (not self.ser or not self.ser.is_open) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        if self.ser and self.ser.is_open:
            self.ser.write(data)
            print(f"[SEND] {data.hex(' ')}")
        else:
            print("[ERROR] 串口未打开，无法发送数据")

    @staticmethod
    def _find_serial_port(exclude_ports=None):
        """
        自动查找可用串口，排除指定端口（如 COM1）

        :param exclude_ports: 要排除的端口列表（如 ['COM1']）
        :return: 第一个可用串口名，或 None
        """
        exclude_ports = exclude_ports or []
        ports = list_ports.comports()
        for port in ports:
            if port.device.upper() not in [e.upper() for e in exclude_ports]:
                return port.device
        return None

enum_baudrate = (cn_serial.Baudrate.BAUDRATE_115200, cn_serial.Baudrate.BAUDRATE_57600, cn_serial.Baudrate.BAUDRATE_38400, cn_serial.Baudrate.BAUDRATE_19200, cn_serial.Baudrate.BAUDRATE_9600)
enum_stopbits = (cn_serial.Stopbits.STOPBITS_ONE, cn_serial.Stopbits.STOPBITS_TWO)
enum_parity = (cn_serial.Parity.PARITY_NONE, cn_serial.Parity.PARITY_EVEN, cn_serial.Parity.PARITY_ODD)

param_baudrate = (115200, 57600, 38400, 19200, 9600)
param_stopbits = (1, 2)
param_parity = ('N', 'E', 'O')

def gen_uart_config_params():
    param_list = []
    for baudrate in param_baudrate:
        for stopbits in param_stopbits:
            for parity in param_parity:
                param_list.append({
                    "baudrate": baudrate,
                    "stopbits": stopbits,
                    "parity": parity
                })
    return param_list

@pytest.fixture
def serial_server(request):
    baudrate, stopbits, parity = request.param["baudrate"], request.param["stopbits"], request.param["parity"]
    dynamic_serial_server = DynamicSerialServer(baudrate=baudrate, stopbits=stopbits, parity=parity)
    dynamic_serial_server.start()
    time.sleep(0.5) # wait for server to be started.
    yield dynamic_serial_server
    dynamic_serial_server.stop()

@pytest.fixture
def cracker_s1():
    s1 = CrackerS1('192.168.0.10')
    s1.connect(force_update_bin=True, force_write_default_config=True)
    s1.uart_io_enable()
    s1.osc_trigger_source('P')
    yield s1
    s1.disconnect()

@pytest.mark.parametrize("serial_server", gen_uart_config_params(), ids=lambda cfg: f"baudrate[{cfg['baudrate']}]-stopbits[{cfg['stopbits']}]-parity[{cfg['parity']}]", indirect=True)
@pytest.mark.parametrize("tx_data_len", [1, 512, 1024, 2048, 4096], ids=lambda x: f"tx_data_len[{x}]")
def test_uart_ts_with_config(cracker_s1, serial_server: DynamicSerialServer, tx_data_len):
    baudrate, stopbits, parity = serial_server.baudrate, serial_server.stopbits, serial_server.parity
    cracker_s1.uart_config(baudrate=enum_baudrate[param_baudrate.index(baudrate)], stopbits=enum_stopbits[param_stopbits.index(stopbits)], parity=enum_parity[param_parity.index(parity)])
    tx_data = os.urandom(tx_data_len)
    status, res = cracker_s1.uart_transmit_receive(tx_data=tx_data, rx_count=len(tx_data), timeout=1000, is_trigger=True)
    print(f"Status: {status}, Response: {res.hex(' ') if res else 'None'}")
    assert res == tx_data

@pytest.mark.parametrize("serial_server", gen_uart_config_params(), ids=lambda cfg: f"baudrate[{cfg['baudrate']}]-stopbits[{cfg['stopbits']}]-parity[{cfg['parity']}]", indirect=True)
@pytest.mark.parametrize("tx_data_len", [1, 512, 1024, 2048, 4096], ids=lambda x: f"tx_data_len[{x}]")
def test_uart_transmit_with_config(cracker_s1, serial_server: DynamicSerialServer, tx_data_len):
    serial_server.response_rules = {b'vvvvvvvvvvvvv': b'vvvvvvvvvvvvv'} # 设置空响应规则，使得其无法发送默认回声响应数据，这样可以读取对端发送的数据
    baudrate, stopbits, parity = serial_server.baudrate, serial_server.stopbits, serial_server.parity
    cracker_s1.uart_config(baudrate=enum_baudrate[param_baudrate.index(baudrate)], stopbits=enum_stopbits[param_stopbits.index(stopbits)], parity=enum_parity[param_parity.index(parity)])
    tx_data = os.urandom(tx_data_len)
    status, res = cracker_s1.uart_transmit(tx_data=tx_data, is_trigger=True)
    assert status == 0, f"Expected status 0 but got {status}"
    received_data = serial_server.get_received_data(tx_data_len)
    assert received_data == tx_data, f"Expected {tx_data.hex(' ')} but got {received_data.hex(' ')}"

@pytest.mark.parametrize("serial_server", gen_uart_config_params(), ids=lambda cfg: f"baudrate[{cfg['baudrate']}]-stopbits[{cfg['stopbits']}]-parity[{cfg['parity']}]", indirect=True)
@pytest.mark.parametrize("rx_data_len", [1], ids=lambda x: f"rx_data_len[{x}]")
def test_uart_receive_with_config(cracker_s1, serial_server: DynamicSerialServer, rx_data_len):
    baudrate, stopbits, parity = serial_server.baudrate, serial_server.stopbits, serial_server.parity
    cracker_s1.uart_config(baudrate=enum_baudrate[param_baudrate.index(baudrate)], stopbits=enum_stopbits[param_stopbits.index(stopbits)], parity=enum_parity[param_parity.index(parity)])
    tx_data = os.urandom(rx_data_len)
    serial_server.send_data(tx_data)
    time.sleep(0.5) # 等待数据接收完成
    status, res = cracker_s1.uart_receive(rx_count=rx_data_len, is_trigger=True)
    assert status == 0, f"Expected status 0 but got {status}"
    assert res == tx_data, f"Expected {tx_data.hex(' ')} but got {res.hex(' ')}"
