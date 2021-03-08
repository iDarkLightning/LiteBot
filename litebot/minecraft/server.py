from ..utils.config import ConfigMap
from .protocol.connection import UDPSocketConnection
from .protocol.query import ServerQuerier, QueryResponse
from .protocol.rcon import ServerRcon
from ..errors import ServerConnectionFailed, ServerNotFound
from socket import timeout

class MinecraftServer:
    """
    Modules communication to and from a minecraft server
    """
    instances = []

    def __init__(self, name: str, **info: ConfigMap) -> None:
        info = ConfigMap(value=info)
        self.name = name
        self._addr = info.numerical_server_ip
        self._port = info.server_port
        self._rcon = ServerRcon(self._addr, info.rcon_password, info.rcon_port)
        self.operator = info.operator
        self.bridge_channel = info.bridge_channel_id
        self.add_instance(self)

    @classmethod
    def add_instance(cls, instance) -> None:
        """
        Appends an instance of the class to a list of instances
        :param instance: The instance to append
        :type instance: MinecraftServer
        """
        cls.instances.append(instance)

    @classmethod
    def get_from_name(cls, name: str):
        """
        Gets a server from its name
        :param name: The name of the server to retrieve
        :type name: str
        :return: An instance of a Minecraft Server
        :rtype: MinecraftServer
        :raises: ServerNotFound
        """
        server = list(filter(lambda s: s.name == name, cls.instances))
        if len(server) > 0:
            return server[0]
        else:
            raise ServerNotFound

    def status(self) -> QueryResponse:
        """
        Gets the status of the server including online players
        :return: A QueryResponse with the server status
        :rtype: QueryResponse
        :raises: ServerConnectionFailed
        """
        try:
            connection = UDPSocketConnection((self._addr, self._port))
            querier = ServerQuerier(connection)
            querier.handshake()
            return querier.read_query()
        except timeout:
            return QueryResponse(status=False)
        except Exception:
            raise ServerConnectionFailed

    def send_command(self, command: str) -> str:
        """
        Executes a command on the server
        :param command: The command to send to the server
        :type command: str
        :return: The server's response to the command
        :rtype: str
        :raises: ServerConnectionFailed
        """
        try:
            self._rcon.connect()
        except ConnectionError:
            raise ServerConnectionFailed

        resp = self._rcon.command(command)

        if resp:
            return resp

    def recieve_message(self):
        pass



