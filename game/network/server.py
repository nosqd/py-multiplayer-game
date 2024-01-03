import socket
import threading
from typing import Callable, Optional, Any, Tuple
from .inetwork import INetwork, recieve_packet
from .packet import PACKETS, Packet


class ConnectedClient:
    def __init__(self, address: Tuple[str, int], connection: socket.socket, on_packet: Callable[[Any, Packet], None]):
        self.socket = connection
        self.address = address
        self.thread = threading.Thread(target=self.work_loop)
        self.on_packet = on_packet
        self.thread.start()

    def work_loop(self):
        while True:
            packet = recieve_packet(self.socket)
            self.on_packet(self, packet)

    def send_packet(self, packet: Packet):
        self.socket.send(packet.pack())


class Server(INetwork):
    def __init__(self, host: str, port: int):
        self.thread = None
        self.handlers = []
        self.socket = None
        self.clients = []
        self.host = host
        self.port = port

    def create(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.thread = threading.Thread(target=self.accept_loop)
        self.socket.listen(127)

    def run(self, callback: Callable[[Optional[Exception]], None]) -> None:
        try:
            self.thread.start()
            callback(None)
        except Exception as e:
            callback(e)

    def on_packet(self, handler: Callable[[ConnectedClient, Packet], None]) -> int:
        self.handlers.append(handler)
        return 0

    def off_packet(self, cid: int) -> None:
        ...
    #  del self.handlers[cid]

    def accept_loop(self):
        while True:
            conn, addr = self.socket.accept()

            client = ConnectedClient(addr, conn, self.on_client_packet)
            self.clients.append(client)
            print(f"Client connected from {addr}")

    def on_client_packet(self, client: ConnectedClient, packet: Packet) -> None:
        print(f"Client {client.address} sent packet {packet.packet_id} ({packet.data})")
        for handler in self.handlers:
            handler(client, packet)

    def handle_error(self, error: Optional[Exception]):
        if error:
            print(f"An error occurred: {error}")

    def broadcast(self, packet: Packet):
        for client in self.clients:
            client.send_packet(packet)
