import socket
import threading
import struct
import sys
import os
import signal
import time


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.nickname = None
        self.multicast_group = ('228.30.30.30', 12345)

        self.write_thread = threading.Thread(target=self.write)
        self.receive_thread = threading.Thread(target=self.receive_by_tcp)
        self.receive_udp_thread = threading.Thread(target=self.receive_by_udp)
        self.receive_multicast_thread = threading.Thread(target=self.receive_by_multicast)

        self.multicast_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.multicast_receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.multicast_receive_socket.bind(('', self.multicast_group[1]))
        mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group[0]), socket.INADDR_ANY)
        self.multicast_receive_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.threads = []
        self.udp_flag = True
        self.tcp_flag = True

    def receive_by_udp(self):
        try:
            while self.running:
                data, addr = self.udp_socket.recvfrom(1024)
                # print(data.decode('utf-8'))
                print(f"[Received by UDP] {data.decode('utf-8')}")
        except socket.error as e:
            if e.errno == 10054:
                print("Connection to the server was lost.")
            else:
                # print(f"[UDP] Error: {e}")
                pass
            self.udp_flag = False
            self.tcp_flag = False
            self.tcp_socket.close()
            self.udp_socket.close()

        except Exception as e:
            # print(f"[UDP] Error: {e}")
            pass
    def send_by_multicast(self, message):
        try:
            message = message.split(' ')
            message = ' '.join(message[:-1])
            self.multicast_send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            self.multicast_send_socket.sendto(message.encode('utf-8'), self.multicast_group)
        except Exception as e:
            # print(f"[Multicast] Send Error: {e}")
            pass

    def receive_by_multicast(self):
        try:
            while self.running:
                print(f"[Received by Multicast] {self.multicast_receive_socket.recv(1024).decode('utf-8')}")
        except Exception as e:
            # print(f"[Multicast] Receive Error: {e}")
            pass

    def send_by_udp(self, message):
        message = message.split(' ')
        message = ' '.join(message[:-1])
        self.udp_socket.sendto(message.encode('utf-8'), (self.host, self.port))

    def receive_by_tcp(self):
        try:
            while self.running:
                message = self.tcp_socket.recv(1024).decode('utf-8')
                message = '[Received by TCP] ' + message
                print(message)
        except socket.error as e:
            if e.errno == 10054:
                print("Connection to the server was lost.")
            else:
                # print(f"[TCP] Error: {e}")
                pass
            self.udp_flag = False
            self.tcp_flag = False
            self.tcp_socket.close()
            self.udp_socket.close()
        except Exception as e:
            # print(f"[TCP] Error: {e}")
            pass
    def send_by_tcp(self, message):
        self.tcp_socket.send(message.encode('utf-8'))

    def write(self):
        try:
            while self.running:
                message = f'{self.nickname}: {input("")}'
                if message.split(' ')[-1] == "-U" or message.split(' ')[-1] == "-u":
                    if self.udp_flag:
                        self.send_by_udp(message)
                    else:
                        print("UDP is not available.")
                elif message.split(' ')[-1] == "-M" or message.split(' ')[-1] == "-m":
                    self.send_by_multicast(message)
                else:
                    if self.tcp_flag:
                        self.send_by_tcp(message)
                    else:
                        print("TCP is not available.")

        except Exception as e:
            # print(f"[TCP] Error: {e}")
            pass
    def signal_handler(self, signum, frame):
        print("Received Ctrl+C. Exiting gracefully.")
        self.running = False

        self.tcp_socket.close()
        self.udp_socket.close()
        self.multicast_send_socket.close()
        self.multicast_receive_socket.close()

        for thread in self.threads:
            if thread.is_alive():
                thread.join()

        sys.exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.nickname = input("Type your nickname: ")
        self.tcp_socket.connect((self.host, self.port))
        self.tcp_socket.send(self.nickname.encode('utf-8'))
        self.udp_socket.sendto(f"UDP_INIT".encode(), (self.host, self.port))

        self.write_thread.start()
        self.receive_thread.start()
        self.threads.append(self.receive_thread)
        self.receive_udp_thread.start()
        self.threads.append(self.receive_udp_thread)
        self.receive_multicast_thread.start()
        self.threads.append(self.receive_multicast_thread)
        self.write_thread.join()


if __name__ == '__main__':
    try:
        host = "127.0.0.1"
        port = 65432
        chat_client = ChatClient(host, port)
        chat_client.start()
    except Exception as e:
        print(f"An error occurred main: {e}")
        sys.exit(1)
