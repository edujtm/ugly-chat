
import enum


class NetConstants(enum.Enum):
    ENCODING = 'utf-8'
    BUFSIZE = 1024


class ProtocolConstants(enum.Enum):
    INIT = 0
    MESSAGE = 1
