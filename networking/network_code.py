from enum import Enum


class Codes(str, Enum):
    OK = "OK"
    FILE_TOO_BIG = "FILE_TOO_BIG"
    INVALID_USERNAME_OR_PASSWORD = "Invalid"
    FAILED_TO_JOIN = "Failed to join"
    NOT_IN_GROUP = "Not in group"
    HAS_GROUP = "Has group"
    GROUP_OWNER = "group owner"
    NOT_GROUP_OWNER = "not group owner"
    ACCEPTED_JOIN_REQUEST = "accepted"
    FINISHED = "Finished"
    FAILED_TO_FIND_FILE = "FAILED_TO_FIND_FILE"
