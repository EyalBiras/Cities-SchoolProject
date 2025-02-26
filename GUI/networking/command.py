from enum import Enum


class Command(str, Enum):
    LOGIN = "login"
    GET_GROUPS = "get groups"
    JOIN_GROUP = "join group"
    LEAVE_GROUP = "leave group"
    IS_IN_GROUP = "is in group"
    CREATE_GROUP = "create group"
    GET_GROUP_MEMBERS = "get group members"
    GET_JOIN_REQUESTS = "get join requests"
    IS_GROUP_OWNER = "is group owner"
    ACCEPT_JOIN_REQUEST = "accept join request"
    GET_FILES = "get files"
    DOWNLOAD_FILE = "download file"
    UPLOAD_FILE = "upload file"
    GET_BATTLES = "Get battles"
    BATTLE = "Battle"
    GET_USER_GROUP = "Get user group"
    DOWNLOAD_BATTLE = "download battle"
    GET_RESULTS = "Get results"
    DOWNLOAD_RESULTS_INFO = "download results game"


