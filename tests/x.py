import socket
import time


def connect_to_server(host='127.0.0.1', port=65432):
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 连接到服务器
        s.connect((host, port))

        print("Connected to the server.")
        print("Type 'quit' to exit.")

        for i in range(1):
            # 用户输入要发送的信息
            message = "Enter your message: " + str(i)

            # 如果用户输入 'quit' 则退出循环
            if message.lower() == 'quit':
                break

            # 发送数据
            s.sendall(message.encode())

            # 接收服务器的响应，一次最多接收1024字节
            data = s.recv(len('Message received'.encode()))

            # 打印服务器的响应
            print(f"Received from server: {data.decode()}")

        time.sleep(50)


if __name__ == "__main__":
    connect_to_server()
