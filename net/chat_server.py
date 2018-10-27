
import socket as sck
import threading as thr
from net.net_constants import NetConstants


def _blocking_clients(fun):
    def block_fn(self, *args):
        self.clients_mutex.acquire()
        fun(self, *args)
        self.clients_mutex.release()

    return block_fn

BUFSIZE = 1024

class ClientListener:
    """
        The listener waits for user messages and handles
        the different kind of messages from the user.
    """
    def __init__(self, sock, cid, server, name=None):
        if name is None:
            name = "Anom"

        self.sock = sock
        self.name = name
        self.client_id = cid
        self.server = server

    def start(self):
        """
            Creates a thread that will listen for client messages.
        :return: None
        """
        thr.Thread(target=self.listen).start()

    def listen(self):
        """
            Method body for message listening thread.
        :return: None
        """
        username = self.get_name()

        self.print("Welcome {}. Type anything to talk to the chat".format(username))
        while True:
            msg = self.sock.recv(1024)
            msg = msg.decode(NetConstants.ENCODING.value)

            self.server.send_message_to_all(msg)

    def print(self, message):
        self.sock.sendall(message.encode(NetConstants.ENCODING.value))

    def get_name(self):
        if self.name == "Anom":
            return self.name + "#" + str(self.client_id)
        else:
            return self.name

    def _handle_protocol(self, data):
        """
            Responsible for handling different kind of messages from the user (private, all),
            configuration options or disconnect requests.

        :param data: The data received from the client socket
        :return: None
        """
        # TODO Create protocol Enum constants and different methods for handling each one of them
        raise NotImplementedError()


class ChatServer:
    """
        This server listen for client connections on the port given by the port param.

        It's also responsible for keeping track of the users currently in the chat room
        and managing messages between them.
    """
    def __init__(self, host='localhost', port=8081):
        """
            Keeps information about the host and port for debuging. The list clients
            keeps track of each user in the room so it's possible to send messages between them

        :param host: The host in which the server will be run on
        :param port: The port where the server will listen for clients
        """
        self.host = host
        self.port = port
        self.clients = []
        self.ID_COUNT = 0

        self.clients_mutex = thr.Lock()
        self.socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)

        self.socket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)

    def start(self):
        """
            Starts listening for new users, Creating a thread for each and
            adding a reference in the clients list attribute

        :return: None
        """
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Server waiting for clients to connect...")
        while True:
            client_socket, client_address = self.socket.accept()

            client_socket.send(bytes('If you\'d like to enter in the chat, please enter your name and press enter', 'utf8'))
            name = client_socket.recv(BUFSIZE).decode('utf8')

            new_client = ClientListener(client_socket, self.ID_COUNT, self, name)
            new_client = ClientListener(client_socket, self.ID_COUNT, self)
            print("Client connected with id: {}".format(self.ID_COUNT))
            self.ID_COUNT += 1

            new_client.start()

            self.clients.append(new_client)
            self.alert_new_client(new_client)

    @_blocking_clients
    def alert_new_client(self, listener):
        """
            Alerts all other users that the user has disconnected
        :param listener: Client listener that entered the chat room
        :return: None
        """
        if not isinstance(listener, ClientListener):
            raise TypeError("The listener parameter must be of the ClientListener class")

        self.send_message_to_all("The user {0} has connected.".format(listener.get_name()))

    @_blocking_clients
    def alert_disconnect(self, listener):
        username = listener.get_name()
        self.clients.remove(listener)

        self.send_message_to_all("The user {0} has disconnected".format(username))

    @_blocking_clients
    def send_message_to_all(self, message):
        for client in self.clients:
            client.print(message)

    @_blocking_clients
    def send_private_message(self, cid, message):
        for client in self.clients:
            if client.id == cid:
                client.print(message)


if __name__ == '__main__':
    import sys

    host = 'localhost'
    port = 8081

    if len(sys.argv) != 3:
        print('Usage: {0} [host-ip] [host-port]'.format(sys.argv[0]))
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    server = ChatServer(host, port)
    server.start()
