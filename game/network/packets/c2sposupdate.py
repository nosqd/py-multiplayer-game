from typing import Tuple
from game.network.packet import Packet, PACKETS


class C2SPositionUpdate(Packet):
    def __init__(self, player_id: int, position: Tuple[int, int]):
        super().__init__(PACKETS.C2S_POSITION_UPDATE, {"position": position, "player_id": player_id})
