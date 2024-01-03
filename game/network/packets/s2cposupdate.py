from typing import Tuple
from game.network.packet import Packet, PACKETS


class S2CPositionUpdate(Packet):
    def __init__(self, player_id: int, position: Tuple[int, int]):
        super().__init__(PACKETS.S2C_POSITION_UPDATE, {"position": position, "player_id": player_id})
