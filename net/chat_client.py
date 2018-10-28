
import threading as thr
import socket as sck
from net.net_constants import NetConstants, ProtocolConstants


class ChatClient:
    def __init__(self, host='localhost', port=8081):

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
        name = input("If you'd like to enter in the chat, please enter your name and press enter\n")
        while True:
            self.send(name)
            response = self.sock.recv(NetConstants.BUFSIZE.value).decode(NetConstants.ENCODING.value)
            if response == ProtocolConstants.NAME_OK.value:
                break
            print(response)

    def _receive(self):
        while True:
            try:
                response = self.sock.recv(NetConstants.BUFSIZE.value)
            except sck.error:
                print("Error occurred while reading data from server")
                break
            if not response:                # Waits for eof from the server. eof is sent when the socket is closed
                print("Quitting chat...")
                break
            print(response.decode(NetConstants.ENCODING.value))

    def _listen(self):
        while True:
            message = input()
            self.send(message)
            if message == "leave()":
                break

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
