
import socket as sck
import threading as thr
from net_constants import NetConstants, ProtocolConstants


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
        thr.Thread(target=self.listen).start()

    def listen(self):
        """
            Method body for message listening thread.
        :return: None
        """
        self._init_name()

        username = self.get_name()
        
        self.print("Welcome {}. Type anything to talk to the chat".format(username))
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

    def change_name(self, newName):
        if self.name == newName:
            self.print('This name is already yours!')
        else:
            self.server.send_message_to_all("The user {0} changed his name to {1}.".format(self.name, newName))
            self.name = newName

    def disconnect(self):
        self.sock.close()

    def _init_name(self):
        # self.print('If you\'d like to enter in the chat, please enter your name and press enter\n')
        name = ''
        while True:
            name = self.sock.recv(NetConstants.BUFSIZE.value).decode('utf8')
            if name not in self.server.names:
                break                
            self.print('This name is already in use, please enter another one!')

        self.print(NetConstants.NAME_OK.value)
        self.server.names.add(name)
        self.print('You can chat now :)')
        self.change_name(name)
    
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
            self.server.send_message_to_all(data)


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
        self.names = set()

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

            new_client = ClientListener(client_socket, client_address, self.ID_COUNT, self)

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

        if not isinstance(listener, ClientListener):
            raise TypeError("The listener parameter must be of the ClientListener class")

        username = listener.get_name()
        listener.disconnect()
        self.clients.remove(listener)

        self.send_message_to_all("The user {0} has disconnected".format(username))

    @_blocking_clients
    def send_message_to_all(self, message):
        for client in self.clients:
            client.print(message)

    @_blocking_clients
    def send_private_message(self, name, message):
        for client in self.clients:
            if client.name == name:
                client.print(message)

    @_blocking_clients
    def listClients(self, isServer, client=None):
        if isServer:
            for client in self.clients:
                print("<{0}, {1}, {2}>".format(client.get_name(), client.sock, client.port))
        elif client is not None:
            for item in self.clients:
                client.print("<{0}, {1}, {2}>".format(item.get_name(), item.sock, item.port))


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

