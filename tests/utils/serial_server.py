import threading
from threading import Thread

import serial
import time
from serial.tools import list_ports


def find_serial_port(exclude_ports=None):
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


def serial_server(
    port=None,
    baudrate=9600,
    bytesize=8,
    stopbits=1,
    parity='N',
    response_rules=None,
    response_delay=0.0
):
    """
    启动基于字节(hex)的串口服务
    """
    if not port:
        port = find_serial_port(exclude_ports=['COM1'])
        if not port:
            print("[ERROR] 未发现可用串口")
            return
        print(f"[INFO] 自动发现串口：{port}")

    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            stopbits=stopbits,
            parity=parity,
            timeout=1
        )

        print(f"[INFO] 串口服务启动：{port}: {baudrate}bps, {bytesize} bits, {stopbits} stopbits, {parity} parity")

        while True:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                if not data:
                    continue

                print(f"[RECV] {data.hex(' ')}")
                print(f"[RECV] {data.decode('utf-8', errors='ignore')}")

                response = None
                if response_rules:
                    response = response_rules.get(data)

                if response:
                    if response_delay > 0:
                        time.sleep(response_delay)
                    ser.write(response)
                    print(f"[SEND] {response.hex(' ')}")
                    print(f"[SEND] {response.decode('utf-8', errors='ignore')}")

    except serial.SerialException as e:
        print(f"[ERROR] 串口错误：{e}")
    except KeyboardInterrupt:
        print("[INFO] 中断退出")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()



# 示例用法
if __name__ == '__main__':
    # rules = {
    #     b'\x01\x02': b'\xAA\xBB',
    #     b'\xFF\x00': b'\xCC\xDD\xEE',
    #     b'\x10':     b'\x20',
    #     b'\x11':     b'\x22'
    # }
    #
    serial_server(
        port=None,  # 自动选择串口
        baudrate=115200,
        bytesize=8,
        stopbits=1,
        parity='O',
        response_rules=None,
        response_delay=3
    )

