from game.network.packet import Packet, PACKETS


class S2CHello(Packet):
    def __init__(self, your_player_id: int):
        super().__init__(PACKETS.S2C_HELLO, {"your_player_id": your_player_id})
