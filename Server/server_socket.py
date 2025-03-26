import pathlib
import re
import shutil

from Server.db.db import DB
from networking import Command
from networking.constants import KILO_BYTE, INVALID_USERNAME_OR_PASSWORD
from networking.network_code import Codes
from networking.socket_wrapper import SocketWrapper
from Server.tournament import battle, run_tournament

DEVELOPMENT_CODE_DIR = "development_code"
ONE_MEGABYTE = 1048576
MAX_SIZE = ONE_MEGABYTE
MAX_SIZE_STR = "1mb"
MAX_AMOUNT_OF_FILES = 40
file = pathlib.Path(__file__)
RESULTS_FILE = file.parent / "results.json"

BASE_PATH = file.parent / "groups"
GAMES_DIRECTORY = file.parent / "games"
TEMPLATE_FILE  = file.parent /"Template.rar"
print(BASE_PATH)
print(GAMES_DIRECTORY)
print(TEMPLATE_FILE)
def is_python(f: pathlib.Path) -> bool:
    return f.name.endswith(".py")

def is_dir_empty(directory: pathlib.Path) -> bool:
    return not (directory.exists() and any(directory.iterdir()))

def get_group_directory(group: str) -> pathlib.Path:
    return BASE_PATH / pathlib.Path(group)

def get_player_enemy(f: pathlib.Path) -> tuple[str, str]:
    pattern = r"([a-zA-Z0-9_]+)\s+vs\s+([a-zA-Z0-9_]+)-winner-[a-zA-Z0-9_]+\.json\.gzip"
    match = re.search(pattern, f.name)
    return match.group(1), match.group(2)

class ServerSocket:
    def __init__(self, server_socket: SocketWrapper, db: DB):
        self.__server_socket = server_socket
        self.db = db

    def receive_message(self, size: int = KILO_BYTE) -> tuple[str, str]:
        x = self.__server_socket.receive_message_secure(size).split(",")
        if x == [""]:
            return "EXIT", "EXIT"
        print(f"{x=}")
        username, password, command, details = x
        print(f"{username=}, {password=}, {command=}, {details=}")
        verification_code = Codes.OK.value

        if command == Command.DOWNLOAD_TEMPLATE.value:
            verification_code = Codes.OK.value
            return_code = Codes.OK.value
            message = Codes.OK.value
            self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code}")
            self.__server_socket.receive_message_secure()
            self.__server_socket.send_file(TEMPLATE_FILE)
            return Codes.OK.value, ""


        if command == Command.SIGN_UP.value:
            if self.db.signup_user(username, password):
                verification_code = Codes.OK.value
                return_code = Codes.OK.value
                message = Codes.OK.value
                self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code}")
                self.__server_socket.receive_message_secure()
                return Codes.OK.value, ""
            else:
                verification_code = Codes.INVALID_USERNAME_OR_PASSWORD.value
                return_code = Codes.INVALID_USERNAME_OR_PASSWORD.value
                message = Codes.INVALID_USERNAME_OR_PASSWORD.value
                self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code}")
                self.__server_socket.receive_message_secure()
                return INVALID_USERNAME_OR_PASSWORD, ""

        if not self.db.validate_user(username, password):
            verification_code = Codes.INVALID_USERNAME_OR_PASSWORD.value
            message = "NO"
            return_code = Codes.INVALID_USERNAME_OR_PASSWORD.value
            self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code}")
            self.__server_socket.receive_message_secure()
            return INVALID_USERNAME_OR_PASSWORD, ""

        message = ""
        return_code = Codes.OK
        if command == Command.BATTLE.value:
            if self.db.is_in_group(username):
                enemy_group = get_group_directory(details)
                group = self.db.get_group(username)
                user_group = get_group_directory(group.name)
                games_directory = user_group / "battles"
                for game in pathlib.Path(games_directory).glob("*"):
                    if details in game.name:
                        shutil.rmtree(game)
                battle(group=user_group, enemy=enemy_group, games_directory=games_directory)
        if command == Command.RUN_TOURNAMENT.value:
            groups = self.db.get_groups()
            message = str(len(groups))
            self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code.value}")
            ack = self.__server_socket.receive_message_secure()
            print(f"{ack=}")
            run_tournament()
            message = Codes.FINISHED.value
            self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code.value}")
            return username, command

        if command == Command.UPLOAD_FILE.value:
            group = self.db.get_group(username)
            f = BASE_PATH / group.name / "development_code" / details
            print(f"{f=}")
            return_code = Codes.OK
            message = ""
            self.__server_socket.send_message_secure(
                f"{verification_code}|{message}|{return_code.value}")
            print(f"got {self.__server_socket.receive_message_secure()}")
            self.__server_socket.receive_file(f)
            # self.__server_socket.receive_message_secure()
            return username, command
        if command == Command.GET_GROUPS.value:
            groups = self.db.get_groups()
            message = f"({str(groups[0])}"
            for group in groups[1:]:
                message += f"),({str(group)}"
            message += ")"
            return_code = Codes.OK
        if command == Command.JOIN_GROUP.value:
            if self.db.ask_for_join_request(username, details):
                return_code = Codes.OK

            else:
                return_code = Codes.FAILED_TO_JOIN

        if command == Command.LEAVE_GROUP.value:
            if self.db.is_in_group(username):
                self.db.leave_group(username)
                return_code = Codes.OK
            else:
                return_code = Codes.NOT_IN_GROUP

        if command == Command.IS_IN_GROUP.value:
            if self.db.is_in_group(username):
                print("In group")
                message = Codes.HAS_GROUP.value
                return_code = Codes.OK
            else:
                message = Codes.NOT_IN_GROUP.value
                return_code = Codes.NOT_IN_GROUP

        if command == Command.CREATE_GROUP.value:
            if self.db.is_in_group(username):
                message = Codes.HAS_GROUP.value
                return_code = Codes.OK
            else:
                self.db.create_group(username, details)
                return_code = Codes.OK

        if command == Command.IS_GROUP_OWNER.value:
            if self.db.is_group_owner(username):
                message = Codes.GROUP_OWNER.value
                return_code = Codes.OK
            else:
                message = Codes.NOT_GROUP_OWNER.value
                return_code = Codes.NOT_GROUP_OWNER

        if command == Command.GET_GROUP_MEMBERS.value:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                message = f"Owner: {group.owner}\n"
                for member in group.users:
                    if member != group.owner:
                        message += f"{member}\n"
                return_code = Codes.OK
            else:
                return_code = Codes.NOT_IN_GROUP
        if command == Command.GET_JOIN_REQUESTS.value:
            if self.db.is_in_group(username):
                join_requests = self.db.get_join_requests(username)
                if join_requests:
                    message = f"{join_requests[0]}"
                    for request in join_requests[1:]:
                        message += f",{request}"
                    return_code = Codes.OK
                else:
                    message = ""
                    return_code = Codes.OK

            else:
                return_code = Codes.NOT_IN_GROUP
        if command == Command.ACCEPT_JOIN_REQUEST.value:
            if self.db.is_asking_for_join_request(details, username):
                self.db.accept_join_request(username, details)
                message = Codes.ACCEPTED_JOIN_REQUEST.value
                return_code = Codes.OK
            else:
                return_code = Codes.NOT_IN_GROUP
        if command == Command.GET_FILES:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                group_directory = get_group_directory(group.name) / DEVELOPMENT_CODE_DIR
                if group_directory.exists():
                    for file_path in group_directory.rglob("*"):
                        if is_python(pathlib.Path(file_path)):
                            message += f"{pathlib.Path(file_path).name},"
                    message = message[:-1]
        if command == Command.DOWNLOAD_RESULTS_INFO:
            group, enemy = details.split("|")
            self.__server_socket.send_message_secure(
                f"{verification_code}|{message}|{return_code.value}")
            self.__server_socket.receive_message_secure()
            for f in GAMES_DIRECTORY.glob("*"):
                file = pathlib.Path(f)
                if group in get_player_enemy(file) and enemy in get_player_enemy(file):
                    print(file.name)
                    print("hi")
                    return_code = Codes.OK
                    self.__server_socket.send_file(file)
            else:
                return_code = Codes.NOT_IN_GROUP
            return username, command
        if command == Command.GET_GROUPS_TO_BATTLE.value:
            for group in BASE_PATH.glob("*"):
                code = group / "tournament_code"
                print(is_dir_empty(code), code)
                if not is_dir_empty(code):
                    message += f"{group.name}|"
            message = message[:-1]
            return_code = Codes.OK
        if command == Command.GET_USER_GROUP:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                message = group.name
                return_code = Codes.OK
            else:
                return_code = Codes.NOT_IN_GROUP
        if command == Command.GET_BATTLES:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                group_directory = get_group_directory(group.name)
                battles_directory = group_directory / "battles"
                message = ""
                if battles_directory.exists():
                    for group in battles_directory.glob("*"):
                        group_dir = pathlib.Path(group)
                        message += group_dir.name + ":"
                        for f in group_dir.rglob("*"):
                            message += f"{f.name},"
                        message = message[:-1]
                        message += "|"
                    message = message[:-1]
                    return_code = Codes.OK
            else:
                return_code = Codes.NOT_IN_GROUP
        if command == Command.GET_RESULTS:
            return_code = Codes.OK
            self.__server_socket.send_message_secure(
                f"{verification_code}|{message}|{return_code.value}")
            self.__server_socket.receive_message_secure()
            self.__server_socket.send_file(RESULTS_FILE)
            return username, command
        if command == Command.DOWNLOAD_BATTLE:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                enemy, file = details.split("/")
                battles = get_group_directory(group.name) / "battles" / enemy / file
                if battles.exists():
                    return_code = Codes.OK
                    self.__server_socket.send_message_secure(
                        f"{verification_code}|{message}|{return_code.value}")
                    self.__server_socket.receive_message_secure()
                    self.__server_socket.send_file(battles)
                    return username, command
        if command == Command.DOWNLOAD_FILE:
            if self.db.is_in_group(username):
                group = self.db.get_group(username)
                group_directory = get_group_directory(group.name) / DEVELOPMENT_CODE_DIR
                if group_directory.exists():
                    for file_path in group_directory.rglob("*"):
                        if file_path.name == details:
                            return_code = Codes.OK
                            self.__server_socket.send_message_secure(
                                f"{verification_code}|{message}|{return_code.value}")
                            self.__server_socket.receive_message_secure()
                            self.__server_socket.send_file(group_directory / file_path)
                            return username, command
            return_code = Codes.FAILED_TO_FIND_FILE

        self.__server_socket.send_message_secure(f"{verification_code}|{message}|{return_code.value}")
        print(f"{self.__server_socket.receive_message_secure()}")
        return username, command

    def send_message(self, message: str) -> Codes:
        self.__server_socket.send_message_secure(message)
        return self.__server_socket.receive_message_secure(KILO_BYTE)

    def send_file(self, file_path: pathlib.Path, chunk_size: int = KILO_BYTE) -> Codes:
        return self.__server_socket.send_file(file_path, chunk_size)
