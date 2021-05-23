import socket, select, ssl, struct, time
from typing import Any, Optional

from litebot.errors import RconException

class ServerRcon(object):
    def __init__(self, host, password, port=25575, tlsmode=0):
        self.socket = None
        self.host = host
        self.password = password
        self.port = port
        self.tlsmode = tlsmode

    def connect(self) -> None:
        """
        Connects to the RCON server via socket
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Enable TLS
        if self.tlsmode > 0:
            ctx = ssl.create_default_context()

            # Disable hostname and certificate verification
            if self.tlsmode > 1:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

            self.socket = ctx.wrap_socket(self.socket, server_hostname=self.host)

        self.socket.connect((self.host, self.port))
        self._send(3, self.password)

    def disconnect(self) -> None:
        """
        Disconnects the socket server
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def _read(self, length: int) -> bytes:
        """
        Reads incoming data
        :param length: The length of the data to read
        :type length: int
        :return: The data that has been recieved
        :rtype: bytes
        """
        data = b""
        while len(data) < length:
            data += self.socket.recv(length - len(data))
        return data

    def _send(self, out_type: int, out_data: str) -> Optional[str]:
        """
        Sends data to the server
        :param out_type: The out type of the data being sent
        :type out_type: int
        :param out_data: The data to send to the server
        :type out_data: str
        :return: The server's response, if any
        :rtype: str
        """
        if self.socket is None:
            raise RconException("Must connect before sending data")

        # Send a request packet
        out_payload = (
            struct.pack("<ii", 0, out_type) + out_data.encode("utf8") + b"\x00\x00"
        )
        out_length = struct.pack("<i", len(out_payload))
        self.socket.send(out_length + out_payload)

        # Read response packets
        in_data = ""
        while True:
            # Read a packet
            (in_length,) = struct.unpack("<i", self._read(4))
            in_payload = self._read(in_length)
            in_id, in_type = struct.unpack("<ii", in_payload[:8])
            in_data_partial, in_padding = in_payload[8:-2], in_payload[-2:]

            # Sanity checks
            if in_padding != b"\x00\x00":
                raise RconException("Incorrect padding")
            if in_id == -1:
                raise RconException("Login failed")

            # Record the response
            in_data += in_data_partial.decode("utf8")

            # If there's nothing more to receive, return the response
            if len(select.select([self.socket], [], [], 0)[0]) == 0:
                return in_data

    def command(self, command) -> Optional[str]:
        """
        Executes a command on the server, and sends the
        response feedback message

        Example
        --------
            codeblock :: python3
                resp = rcon.command("whitelist add Steve")

        :param command: The cmmand to send to the server
        :type command: str
        :return: The server's response
        :rtype: str
        """
        result = self._send(2, f"/{command}")
        time.sleep(0.003)  # MC-72390 workaround
        return result
