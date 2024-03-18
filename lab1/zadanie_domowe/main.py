from server import ChatServer

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 65432
    server = ChatServer(HOST, PORT)
    server.start()