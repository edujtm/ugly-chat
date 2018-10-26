
import threading as thr
import socket as sck


class ChatClient:
    # TODO create a disconnect message that will end the listen and receive threads
    def __init__(self, host='localhost', port=8081):

        # TODO Maybe use makefile on socket so it uses a simpler interface
        self.sock = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        self.host = host
        self.port = port

        # TODO create mutex to avoid sending an receiving messages at the same time
        #self.message_mutex = mutex
        pass

    def start(self):
        self.sock.connect((self.host, self.port))
        receiver = thr.Thread(target=self._receive).start()
        listener = thr.Thread(target=self._listen).start()

        receiver.join()
        listener.join()

    def _receive(self):
        while True:
            response = self.sock.recv(1024)
            print(response)

    def _listen(self):
        while True:
            message = input("Type your message")
            self.sock.sendall(bytearray(message))


if __name__ == '__main__':
    pass
