import socket
import threading
import sys, os, signal, time
class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.clients_udp = set()
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.threads = []
        self.running = True

    def broadcastTcp(self, message, from_socket):
        for client_socket, (nickname, address) in list(self.clients.items()):
            try:
                if client_socket != from_socket and not client_socket._closed:
                    client_socket.send(message)
            except (BrokenPipeError, ConnectionResetError):
                print(f"Connection with {nickname} at {address} lost.")
                self.clients.pop(client_socket)
                client_socket.close()

    def broadcastUdp(self, message, from_address):
        for client_address in self.clients_udp:
            try:
                if client_address != from_address:
                    self.udp_server_socket.sendto(message, client_address)
            except (OSError, socket.error) as e:
                print(f"Error sending UDP message to {client_address}: {e}")
                self.clients_udp.remove(client_address)

    def handleUdp(self):
        while self.running:
            try:
                data, addr = self.udp_server_socket.recvfrom(1024)
                if data == b'UDP_INIT':
                    print(f"UDP connection from {addr}")
                    self.clients_udp.add(addr)
                elif addr in self.clients_udp:
                    self.broadcastUdp(data, addr)
            except ConnectionResetError:
                # print("UDP LEFT")
                pass
            except Exception as e:
                # print("UDP LEFT")
                # print(f"Error: {e}")
                pass

    def handleTcp(self, client_socket):
        try:
            while self.running:
                message = client_socket.recv(1024)
                if not message:
                    break
                self.broadcastTcp(message, client_socket)
        except Exception as e:
            # print(f"handleTcp Error: {e}")
            pass
        nickname = self.clients.get(client_socket, ("Unknown", "Unknown"))[0]
        print(f"{nickname} left!")
        self.broadcastTcp(f'{nickname} left!'.encode('utf-8'), client_socket)

        if client_socket in self.clients:
            self.clients.pop(client_socket)

        client_socket.close()
    def signal_handler(self, signum, frame):
        print("Received Ctrl+C. Exiting gracefully.")
        self.running = False

        self.tcp_server_socket.close()
        self.udp_server_socket.close()
        for client_socket in self.clients:
            client_socket.close()

        for thread in self.threads:
            if thread.is_alive():
                thread.join()

        sys.exit(0)

    def initialize(self):
        try:
            while self.running:
                client_socket, client_address = self.tcp_server_socket.accept()
                print(f"Connected with {client_address}")
                nickname = client_socket.recv(1024).decode('utf-8')
                self.clients[client_socket] = (nickname, client_address)

                print("Nickname is: {}\n".format(nickname))
                self.broadcastTcp("{} joined!".format(nickname).encode('utf-8'), client_socket)
                client_socket.send('\n You are connected to the server!'.encode('utf-8'))

                client_thread = threading.Thread(target=self.handleTcp, args=(client_socket,))
                client_thread.start()
                self.threads.append(client_thread)

        except Exception as e:
            # print(f"Error in initialize: {e}")
            pass


    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.tcp_server_socket.bind((self.host, self.port))
        self.udp_server_socket.bind((self.host, self.port))

        print(f"Chat server starting")
        self.tcp_server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")

        udp_thread = threading.Thread(target=self.handleUdp)
        udp_thread.start()
        self.threads.append(udp_thread)
        initialize_thread = threading.Thread(target=self.initialize)
        initialize_thread.start()
        self.threads.append(initialize_thread)
        while self.running:
            pass
