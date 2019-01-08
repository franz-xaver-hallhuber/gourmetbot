import socket

PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))
data, addr = s.recvfrom(1024)
print(data)
