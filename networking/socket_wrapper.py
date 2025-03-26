import pathlib
import socket
import ssl
from networking.constants import KILO_BYTE
from networking.network_code import Codes


class SocketWrapper:
    def __init__(self, _socket: socket.socket, encoding: str = "utf-8", use_ssl: bool = False):
        self.__encoding = encoding
        self.__socket = _socket


    def send_message_secure(self, message: str) -> None:
        self.__socket.sendall(message.encode(self.__encoding))

    def receive_message_secure(self, size: int = KILO_BYTE) -> str:
        return self.__socket.recv(size).decode(self.__encoding)

    def receive_message_secure_bytes(self, size: int = KILO_BYTE) -> bytes:
        return self.__socket.recv(size)

    def send_file(self, file_path: pathlib.Path, chunk_size: int = KILO_BYTE) -> Codes:
        self.send_message_secure(file_path.name)
        ack = self.receive_message_secure()

        file_size = file_path.stat().st_size
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        self.send_message_secure(f"{chunk_size}|{total_chunks}")
        ack = self.receive_message_secure()

        with open(file_path, "rb") as f:
            for _ in range(total_chunks):
                chunk = f.read(chunk_size)
                self.__socket.sendall(chunk)
                ack = self.receive_message_secure()
        return self.receive_message_secure()

    def receive_file(self, save_file: pathlib.Path = "", chunk_size: int = KILO_BYTE,
                     max_file_size: int = 300 * KILO_BYTE) -> bool:
        file_name = self.receive_message_secure()
        print(f"{file_name=}")
        save_file = pathlib.Path(save_file or file_name)

        self.send_message_secure(Codes.OK.value)
        message = self.receive_message_secure()
        print(f"{message=}")
        chunk_size, num_chunks = message.split("|")
        chunk_size = int(chunk_size)
        num_chunks = int(num_chunks)
        self.send_message_secure(Codes.OK.value)

        save_file.parent.mkdir(parents=True, exist_ok=True)

        with open(save_file, "wb") as f:
            for _ in range(num_chunks):
                chunk = self.receive_message_secure_bytes(chunk_size)
                f.write(chunk)
                self.send_message_secure(Codes.OK.value)
        self.send_message_secure(Codes.OK.value)
