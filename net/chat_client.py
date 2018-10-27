
import threading as thr
import socket as sck
from net_constants import NetConstants


class ChatClient:
    def __init__(self, host='localhost', port=8081):

        # TODO Maybe use makefile on socket so it uses a simpler interface
        self.sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.host = host
        self.port = port

    def start(self):
        self.sock.connect((self.host, self.port))
        self._handle_name()

        receiver = thr.Thread(target=self._receive)
        listener = thr.Thread(target=self._listen)

        receiver.start()
        listener.start()
        receiver.join()
        listener.join()

    def _handle_name(self):
        while True:
            # TODO synchronize this method with server (for each recv there must be an send and vice-versa)
            name = input("If you'd like to enter in the chat, please enter your name and press enter\n")
            self.send(name)
            data = self.sock.recv(NetConstants.BUFSIZE.value)
            if data.decode(NetConstants.ENCODING.value) == NetConstants.NAME_OK.value:
                break

    def _receive(self):
        while True:
            try:
                response = self.sock.recv(NetConstants.BUFSIZE.value)
            except sck.error:
                print("Error occurred while reading data from server")
                break
            print(response.decode(NetConstants.ENCODING.value))

    def _listen(self):
        while True:
            message = input("Type your message: ")
            self.sock.sendall(message.encode(NetConstants.ENCODING.value))

    def send(self, data):
        self.sock.sendall(data.encode(NetConstants.ENCODING.value))


if __name__ == '__main__':
    import sys

    host = 'localhost'
    port = 8081

    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
    elif len(sys.argv) == 2:
        host = sys.argv[1]
    elif len(sys.argv) > 3:
        print("Usage: {} [server-ip] [server-port]".format(sys.argv[0]))

    print("Creating client at host: {0} and port: {1}".format(host, port))

    client = ChatClient(host, port)
    client.start()
