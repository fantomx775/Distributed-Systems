import socket;

serverPort = 9009
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
buff = []

print('PYTHON UDP SERVER')

while True:

    buff, address = serverSocket.recvfrom(1024)
    if buff == b'python':
        print('python')
    if buff == b'java':
        print('java')




