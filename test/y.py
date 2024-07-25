import socket


def start_server(host='127.0.0.1', port=65432):
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 绑定到指定的主机和端口
        s.bind((host, port))

        # 开始监听，参数是最大排队连接数
        s.listen()

        print(f"Server is listening on {host}:{port}")

        while True:
            # 接受客户端连接，返回新的socket对象和客户端地址
            conn, addr = s.accept()

            with conn:
                print(f"Connected by {addr}")
                while True:

                    # 读取客户端发送的数据，一次最多读取1024字节
                    data = conn.recv(1024)

                    if not data:
                        print(f"Connection closed by {addr}")
                        break

                    # 打印接收到的数据
                    print(f"Received: {data.decode()}")

                    # 发送响应给客户端
                    response = "Message received".encode()
                    conn.sendall(response)
                print(f'Disconnected from {addr}')


if __name__ == "__main__":
    start_server()