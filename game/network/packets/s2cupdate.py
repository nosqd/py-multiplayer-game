from typing import Tuple, List, Any
from game.network.packet import Packet, PACKETS


class S2CFullUpdate(Packet):
    def __init__(self, players: List[Any]):
        super().__init__(PACKETS.S2C_FULL_UPDATE, {"players": players})
