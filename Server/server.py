import socket
import ssl
import threading

from networking import SocketWrapper
from Server.server_socket import ServerSocket
from db.db import DB
CERT_FILE = "server-cert.pem"
KEY_FILE = "server-key.pem"

def handle_client(client_socket, db):
    s = ServerSocket(SocketWrapper(client_socket), db)
    while True:
        username, command = s.receive_message()
        if username == "EXIT" and command == "EXIT":
            break
        print(f"details: \n\t{username=}\n\t{command=}")


host = '127.0.0.1'
port = 8081
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(5)
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

sock = context.wrap_socket(sock, server_side=True)

db = DB()

print('Initiating clients')
while True:
    client_socket, addr = sock.accept()
    print(f"Got connection from {addr}!")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, db))
    client_thread.daemon = True
    client_thread.start()
