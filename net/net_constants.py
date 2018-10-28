
import enum


class NetConstants(enum.Enum):
    ENCODING = 'utf-8'
    BUFSIZE = 1024

class ProtocolConstants(enum.Enum):
    NAME_OK = 'NAME_OK'
    CLOSE_CONN = "#CLOSE"
