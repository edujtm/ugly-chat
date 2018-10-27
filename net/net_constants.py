
import enum


class NetConstants(enum.Enum):
    ENCODING = 'utf-8'
    BUFSIZE = 1024
    NAME_OK = 'NAME_OK'

class ProtocolConstants(enum.Enum):
    CHANGE_NAME = "name"
    MESSAGE = 1
