
import threading as thr
import socket as sck
from net.net_constants import NetConstants


class ChatClient:
    # TODO create a disconnect message that will end the listen and receive threads
    def __init__(self, host='localhost', port=8081):

        # TODO Maybe use makefile on socket so it uses a simpler interface
        self.sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.host = host
        self.port = port

    def start(self):
        self.sock.connect((self.host, self.port))
        receiver = thr.Thread(target=self._receive)
        listener = thr.Thread(target=self._listen)

        receiver.start()
        listener.start()

        receiver.join()
        listener.join()

    def _receive(self):
        while True:
            try:
                response = self.sock.recv(1024)
            except sck.error:
                print("Error occurred while reading data from server")
                break
            print(response.decode(NetConstants.ENCODING.value))

    def _listen(self):
        while True:
            message = input("Type your message")
            self.sock.sendall(message.encode(NetConstants.ENCODING.value))


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
