import socket
import threading
from typing import Callable, Optional
from .inetwork import INetwork, recieve_packet
from .packet import Packet
from .packets import C2SHello


class Client(INetwork):
    def __init__(self, host: str, port: int):
        self.thread = None
        self.handlers = []
        self.socket = None
        self.host = host
        self.port = port

    def create(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = threading.Thread(target=self.receive_loop)
        self.socket.connect((self.host, self.port))
        self.send_packet(C2SHello())

    def send_packet(self, packet: Packet):
        self.socket.send(packet.pack())

    def run(self, callback: Callable[[Optional[Exception]], None]) -> None:
        try:
            self.thread.start()
            callback(None)
        except Exception as e:
            callback(e)

    def on_packet(self, handler: Callable[[Packet], None]) -> int:
        self.handlers.append(handler)
        return 0

    def off_packet(self, cid: int) -> None:
        ...

    def receive_loop(self):
        while True:
            packet = recieve_packet(self.socket)
            if packet is not None:
                for handler in self.handlers:
                    handler(packet)
