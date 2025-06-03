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

            # print(f"[INFO] 串口服务启动：{self.port} @ {self.baudrate}bps (byte 模式)")

            while self._running:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if not data:
                        continue

                    # print(f"[RECV] {data.hex(' ')}")

                    response = None
                    if self.response_rules:
                        response = self.response_rules.get(data)
                    else:
                        response = data

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
def cracker_s1(request):
    s1 = CrackerS1('192.168.0.10')
    s1.connect(force_update_bin=True, force_write_default_config=True)
    s1.uart_io_enable()
    s1.osc_trigger_source('P')
    yield s1
    s1.disconnect()

@pytest.mark.parametrize("serial_server", gen_uart_config_params(), ids=lambda cfg: f"{cfg['baudrate']}-{cfg['stopbits']}-{cfg['parity']}", indirect=True)
def test_uart_ts_with_config(cracker_s1, serial_server: DynamicSerialServer):
    baudrate, stopbits, parity = serial_server.baudrate, serial_server.stopbits, serial_server.parity
    cracker_s1.uart_config(baudrate=enum_baudrate[param_baudrate.index(baudrate)], stopbits=enum_stopbits[param_stopbits.index(stopbits)], parity=enum_parity[param_parity.index(parity)])
    tx_data = bytes.fromhex('11 22')
    status, res = cracker_s1.uart_transmit_receive(tx_data=tx_data, rx_count=len(tx_data), timeout=1000, is_trigger=True)
    print(f"Status: {status}, Response: {res.hex(' ') if res else 'None'}")
    assert res == tx_data
