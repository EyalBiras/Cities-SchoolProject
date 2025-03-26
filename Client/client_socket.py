import pathlib

from networking.command import Command
from networking.constants import KILO_BYTE
from networking.network_code import Codes
from networking.socket_wrapper import SocketWrapper


class ClientSocket:
    def __init__(self, client_socket: SocketWrapper):
        self.__client_socket = client_socket
        self.username = ""
        self.password = ""

    def validate_user(self) -> bool:
        return_code, _ = self.send_command(Command.LOGIN)
        print(return_code)
        return return_code == Codes.OK

    def sign_up(self) -> bool:
        return_code, _ = self.send_command(Command.SIGN_UP)
        print(return_code)
        return return_code == Codes.OK

    def send_command(self, command: Command, details: str = "") -> tuple[Codes, str]:
        print(f"{command=}")
        self.__client_socket.send_message_secure(f"{self.username},{self.password},{command.value},{details}")
        x = self.__client_socket.receive_message_secure(KILO_BYTE)
        print(f"{command=},{x=}")
        verfication_code = x[:x.find("|")]
        message = x[x.find("|") + 1:x.rfind("|")]
        return_code = x[x.rfind("|") + 1:]
        self.__client_socket.send_message_secure(Codes.OK.value)
        return return_code, message

    def receive_message(self, size: int = KILO_BYTE) -> str:
        return self.__client_socket.receive_message_secure(size)

    def send_message(self, message: str) -> Codes:
        if self.validate_user():
            self.__client_socket.send_message_secure(message)
            return self.__client_socket.receive_message_secure(KILO_BYTE)
        return Codes.INVALID_USERNAME_OR_PASSWORD

    def send_file(self, file_path: pathlib.Path, chunk_size: int = KILO_BYTE) -> Codes:
        return self.__client_socket.send_file(file_path, chunk_size)

    def receive_file(self, file_path: pathlib.Path = "") -> Codes:
        self.__client_socket.receive_file(file_path)
