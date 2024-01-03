from game.network.packet import Packet, PACKETS


class C2SHello(Packet):
    def __init__(self):
        super().__init__(PACKETS.C2S_HELLO, {"hello": "world"})
