import socket

from nutcracker.cracker import protocol
from nutcracker.cracker.protocol import *


def handle_message(conn):
    while True:
        # 接收协议头
        header_data: bytes = conn.recv(REQ_HEADER_SIZE)

        if not header_data:
            break
        elif not header_data.startswith(protocol.MAGIC_STR):
            print("Receive not header", header_data.decode('utf-8'))
            conn.sendall(header_data)
        else:
            magic, version, direction, command, rfu, length = struct.unpack(
                REQ_HEADER_FORMAT, header_data
            )

            print(
                f"Received header: Magic={magic}, Version={version}, Direction={direction}, Command={command}, Length={length}"
            )

            # 根据length接收Payload
            payload = conn.recv(length)
            message = payload.decode("ascii")
            print(f"Payload: {message}")

            # 假设简单的响应：回显大写message
            response = message.upper()
            response_payload = response.encode("ascii")
            response_header = struct.pack(
                RESP_HEADER_FORMAT,
                b"AHCC",
                1,
                b"R",
                STATUS_OK,
                len(response_payload),
            )
            conn.sendall(response_header + response_payload)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12345))  # 绑定到本地的12345端口
    server_socket.listen()
    print("Server is listening...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")
        handle_message(conn)
        print(f"Disconnected by {addr}")


if __name__ == "__main__":
    start_server()
