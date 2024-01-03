from typing import Callable, Optional
from .packet import Packet, PACKETS
import socket


class INetwork:
    def create(self) -> None:
        pass

    def run(self, callback: Callable[[Optional[Exception]], None]) -> None:
        pass

    def on_packet(self, handler: Callable[[Packet], None]) -> int:
        pass

    def off_packet(self, callback_id: int) -> None:
        pass


def recieve_packet(connection: socket.socket) -> Packet | None:
    raw_header = connection.recv(Packet.HEADER_SIZE)
    if not raw_header:
        return None
    header = Packet.unpack_header(raw_header)
    raw_packet = connection.recv(header[2])
    packet = Packet.unpack(header, raw_packet)
    return packet
