
import sys
import socket as sck
import threading as thr
from net.net_constants import NetConstants, ProtocolConstants


def _blocking_clients(fun):
    def block_fn(self, *args):
        self.clients_mutex.acquire()
        fun(self, *args)
        self.clients_mutex.release()
    return block_fn


def _strip_content(data):
    separator = data.find('(')
    protocol, content = data[:separator], data[separator+1:-1]
    return protocol, content


class ClientListener:
    """
        The listener waits for user messages and handles
        the different kind of messages from the user.
    """
    def __init__(self, sock, port, cid, server, name=None):
        if name is None:
            name = "Anom"

        self.sock = sock
        self.port = port
        self.name = name
        self.client_id = cid
        self.server = server

    def start(self):
        """
            Creates a thread that will listen for client messages.
        :return: None
        """
        listen = thr.Thread(target=self.listen)
        listen.start()

    def listen(self):
        """
            Method body for message listening thread.
        :return: None
        """

        self._init_name()
        self.server.alert_new_client(self)

        username = self.get_name()

        self.print("Welcome {}. Type anything to talk to the chat.\n".format(username))
        while True:
            msg = self.sock.recv(1024)

            decoded = msg.decode(NetConstants.ENCODING.value)
            self._handle_protocol(decoded)

    def print(self, message):
        self.sock.sendall(message.encode(NetConstants.ENCODING.value))

    def get_name(self):
        if self.name == "Anom":
            return self.name + "#" + str(self.client_id)
        else:
            return self.name

    def change_name(self, newName, broadcast=True):
        if self.name == newName:
            self.print('This name is already yours!\n')
        else:
            if broadcast:
                self.server.send_message_to_all("The user {0} changed his name to {1}.\n".format(self.name, newName))
            self.name = newName

    def disconnect(self):
        self.sock.close()
        sys.exit()

    def _init_name(self):
        name = ''
        while True:
            name = self.sock.recv(NetConstants.BUFSIZE.value).decode('utf8')
            if name not in self.server.clients.keys():
                break                
            self.print('This name is already in use, please enter another one!\n')

        self.print(ProtocolConstants.NAME_OK.value)
        self.server.clients[name] = self
        self.change_name(name, broadcast=False)
        self.print('You can chat now :)')
    
    def _handle_protocol(self, data):
        """
            Responsible for handling different kind of messages from the user (private, all),
            configuration options or disconnect requests.

        :param data: The data received from the client socket
        :return: None
        """

        protocol, content = _strip_content(data)

        if protocol == 'name':
            self.change_name(content)
        elif protocol == 'list':
            self.server.listClients(False, self)
        elif protocol == 'private':
            # TODO
            pass
        elif protocol == 'leave':
            self.server.alert_disconnect(self)
        else:
            self.server.messages.append((self.get_name(), data))
            self.server.send_message_to_all(self.get_name() + ': ' + data)


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

            The clients dictionary will contain a mapping from each unique username to the client
            listener that will listen for request of that user.

        :param host: The host in which the server will be run on
        :param port: The port where the server will listen for clients
        """
        self.host = host
        self.port = port
        self.clients = {}
        self.ID_COUNT = 0

        self.clients_mutex = thr.Lock()
        self.socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)

        self.socket.setsockopt(sck.SOL_SOCKET, sck.SO_REUSEADDR, 1)

        self.messages = []

    def start(self):
        """
            Starts listening for new users, Creating a thread for each and
            adding a reference in the clients list attribute

        :return: None
        """
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Server waiting for clients to connect...\n")
        while True:
            client_socket, client_address = self.socket.accept()

            new_client = ClientListener(client_socket, client_address, self.ID_COUNT, self)

            print("Client connected with id: {}\n".format(self.ID_COUNT))
            self.ID_COUNT += 1

            new_client.start()

    def alert_new_client(self, listener):
        """
            Alerts all other users that the user has disconnected
        :param listener: Client listener that entered the chat room
        :return: None
        """
        if not isinstance(listener, ClientListener):
            raise TypeError("The listener parameter must be of the ClientListener class")

        self.send_message_to_all("The user {0} has connected.\n".format(listener.get_name()))

    def alert_disconnect(self, listener):

        if not isinstance(listener, ClientListener):
            raise TypeError("The listener parameter must be of the ClientListener class")

        username = listener.get_name()
        self.clients.pop(username)

        quit_message = "The user {0} has disconnected.\n".format(username)
        print(quit_message)
        self.send_message_to_all(quit_message)
        listener.disconnect()

    def send_message_to_all(self, message):
        for username, client in self.clients:
            client.print(message)

    def send_private_message(self, client_sending, name, message):
        try:
            self.clients[name].print(message)
        except KeyError:
            client_sending.print("User is not present in this chat room")

    def listClients(self, isServer, client=None):
        if isServer:
            for client in self.clients:
                print("<{0}, {1}, {2}>".format(client.get_name(), client.port[0], client.port[1]))
        elif client is not None:
            for username, item in self.clients:
                client.print("<{0}, {1}, {2}>".format(username, item.port[0], item.port[1]))


if __name__ == '__main__':
    import sys

    host = 'localhost'
    port = 8081

    if len(sys.argv) != 3:
        print('Usage: {0} [host-ip] [host-port]\n'.format(sys.argv[0]))
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    server = ChatServer(host, port)

    startThr = thr.Thread(target=server.start())
    startThr.start()
    startThr.join()

