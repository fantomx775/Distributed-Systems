import socket

serverIP = "127.0.0.1"
serverPort = 9008
msg = (300).to_bytes(4, byteorder='little')

print('PYTHON UDP CLIENT')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(msg, (serverIP, serverPort))

response, server_address = client.recvfrom(1024)
received_int = int.from_bytes(response, byteorder='little')
print('Received response from server:', received_int)
client.close()