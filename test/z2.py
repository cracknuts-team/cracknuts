import socket

# 创建一个socket对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 建立连接
s.connect(('127.0.0.1', 65432))

# 发送数据
s.sendall(b'GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n')

# 接收数据
chunk_size = 4096
complete_data = b''

while True:
    data = s.recv(chunk_size)
    if data:
        complete_data += data
    else:
        break

# 打印接收到的数据
print(complete_data)

# 关闭连接
s.close()
