import socket
import struct
from ipaddress import ip_address
from typing import Any, Optional


def ip_type(address: str) -> Optional[str]:
    """
    Checks the type of the IP address
    :param address: The address to the server
    :type address: str
    :return: The type of the IP address
    :rtype: Optional[str]
    """
    try:
        return ip_address(address).version
    except ValueError:
        return

class Connection:
    def __init__(self):
        self.sent = bytearray()
        self.received = bytearray()

    def read(self, length: int) -> bytes:
        """
        Reads the recieved packet
        :param length: The amount of bytes to read
        :type length: int
        :return: The data from the recieved packet
        :rtype: bytes
        """
        result = self.received[:length]
        self.received = self.received[length:]
        return result

    def write(self, data: Any) -> None:
        """
        Writes data to the outgoing packet
        :param data: The data to write
        :type data: Any
        """
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        if isinstance(data, str):
            data = bytearray(data)
        self.sent.extend(data)

    def receive(self, data: Any) -> None:
        """
        Recieves data from the connection
        :param data: The data in the form of a bytearray
        :type data: Any
        """
        if not isinstance(data, bytearray):
            data = bytearray(data)
        self.received.extend(data)

    def remaining(self) -> int:
        """
        Returns the length of the remaining data
        :return: Length of the remaining data
        :rtype: int
        """
        return len(self.received)

    def flush(self) -> str:
        """
        Sends all data that hasn't been sent yet
        :return: The data that has been sent
        :rtype: str
        """
        result = self.sent
        self.sent = ""
        return result

    def _unpack(self, format_: str, data: Any) -> tuple:
        """
        Unpacks the binary data to original representation
        :param format_: The original representation form of the data
        :type format_: str
        :param data: The data to unpack
        :type data: bytes
        :return: The data in the given format
        :rtype: Tuple
        """
        return struct.unpack(">" + format_, bytes(data))[0]

    def _pack(self, format_: str, data: Any) -> bytes:
        """
        Converts the given data into into its binary representation
        :param format_: The format the data will be once converted
        :type format_: str
        :param data: The data to convert
        :type data: Any
        :return: The converted data
        :rtype: bytes
        """
        return struct.pack(">" + format_, data)

    def read_ascii(self) -> str:
        """
        Reads ascii from recieved data
        :return: The data decored from bytes
        :rtype: str
        """
        result = bytearray()
        while len(result) == 0 or result[-1] != 0:
            result.extend(self.read(1))
        return result[:-1].decode("ISO-8859-1")

    def write_int(self, value: int) -> None:
        """
        Writes an integer to ougoing data
        :param value: The integer to write
        :type value: int
        """
        self.write(self._pack("i", value))

    def write_uint(self, value: int) -> None:
        """
        Writes a UINT value to outgoing data
        :param value: The UINT to write
        :type value: int
        """
        self.write(self._pack("I", value))

class UDPSocketConnection(Connection):
    REMAINING = 65535

    def __init__(self, addr: tuple[str, int], timeout: int = 3) -> None:
        Connection.__init__(self)
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def read(self, length: int) -> Any:
        """
        Reads incoming data
        :param length: The length in bytes of the data
        :type length: int
        :return: The data recieved
        :rtype: Any
        """
        result = bytearray()
        while len(result) == 0:
            result.extend(self.socket.recvfrom(UDPSocketConnection.REMAINING)[0])
        return result

    def write(self, data: Any) -> None:
        """
        Writes ougoing data
        :param data: The data to write
        :type data: Any
        """
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        self.socket.sendto(data, self.addr)
