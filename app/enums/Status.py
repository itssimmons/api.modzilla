from enum import Enum


class Status(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    IDLE = "idle"
    TYPING = "typing"
