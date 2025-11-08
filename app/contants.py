from enum import Enum


class AllowedExtensions(Enum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    WEBP = "image/webp"
    MP4 = "video/mp4"
    WEBM = "video/webm"


class Roles(Enum):
    STAFF = "staff"
    DEFAULT = "default"


class Status(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    IDLE = "idle"
    TYPING = "typing"
