import struct
from .connection import Connection

class QueryResponse:
    """
    Models the response data from a query request response
    """
    class Players:
        def __init__(self, names, max_=100):
            self.online = len(names)
            self.max = int(max_)
            self.names = names

        def __iter__(self):
            for name in self.names:
                yield name

        def __len__(self):
            return len(self.names)

        def __repr__(self):
            return str(self.names)

    def __init__(self, **data):
        if not data["status"]:
            self.online = data["status"]
            self.motd = None
            self.players = QueryResponse.Players([])
            return

        self.online = data["status"]
        self.motd = data["raw"]["hostname"]
        self.players = QueryResponse.Players(data["players"], data["raw"]["maxplayers"])

    def __repr__(self):
        return f"<QueryResponse status={self.online}, motd={self.motd}, players={self.players}>"

class ServerQuerier:
    MAGIC_PREFIX = bytearray.fromhex("FEFD")
    PACKET_TYPE_CHALLENGE = 9
    PACKET_TYPE_QUERY = 0

    def __init__(self, connection):
        self.connection = connection
        self.challenge = 0

    def _create_packet(self, id_: int) -> Connection:
        """
        Creates a packet to send to the server
        :param id_: The ID to write to the packet
        :type id_: int
        :return: A new packet, instance of Connection
        :rtype: Connection
        """
        packet = Connection()
        packet.write(self.MAGIC_PREFIX)
        packet.write(struct.pack("!B", id_))
        packet.write_uint(0)
        packet.write_int(self.challenge)
        return packet

    def _read_packet(self) -> Connection:
        """
        Reads a packet from the server
        :return: A new packet with the response from the server
        :rtype: Connection
        """
        packet = Connection()
        packet.receive(self.connection.read(self.connection.remaining()))
        packet.read(1 + 4)
        return packet

    def handshake(self) -> None:
        """
        Performs a handshake between the client and the server
        """
        self.connection.write(self._create_packet(self.PACKET_TYPE_CHALLENGE))

        packet = self._read_packet()
        self.challenge = int(packet.read_ascii())

    def read_query(self) -> QueryResponse:
        """
        Makes a query to the server and returns the response
        :return: A QueryResponse object with the data from the query
        :rtype: QueryResponse
        """
        request = self._create_packet(self.PACKET_TYPE_QUERY)
        request.write_uint(0)
        self.connection.write(request)

        response = self._read_packet()
        response.read(len("splitnum") + 1 + 1 + 1)
        data = {}
        players = []

        while True:
            key = response.read_ascii()
            if len(key) == 0:
                response.read(1)
                break
            value = response.read_ascii()
            data[key] = value

        response.read(len("player_") + 1 + 1)

        while True:
            name = response.read_ascii()
            if len(name) == 0:
                break
            players.append(name)

        return QueryResponse(raw=data, players=players, status=True)
