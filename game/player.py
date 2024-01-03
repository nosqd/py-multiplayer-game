import pygame as pg
from typing import Tuple
from .network.inetwork import Packet
from .network.packet import PACKETS
from .network.packets import C2SPositionUpdate
from .utils.game_factory import GAME_FACTORY
from .utils.vec_utils import vec2_distance

class Player:
    _pos = (0, 0)
    _name = ""
    _local = True
    _uid = 0
    _parent = None

    def __init__(self, position: Tuple[int, int], name: str, is_local: bool, player_id: int = 0, parent=None):
        self._pos = position
        self._name = name
        self._local = is_local
        self._uid = player_id
        self._parent = parent
        self.old_pos = position

    def draw(self, surface: pg.surface.Surface):
        pg.draw.circle(surface, (255, 255, 255), (self._pos[0], self._pos[1]), 50)

    def tick(self):
        if self.is_local:
            mouseX, mouseY = pg.mouse.get_pos()
            self._pos = mouseX, mouseY
            if vec2_distance(self._pos, self.old_pos) >= 50:
                self._parent.network.send_packet(C2SPositionUpdate(self.player_id, self.position))
                self.old_pos = self._pos
        else:
            # packet deque
            for p in self._parent.packet_queue:
                if p.data["player_id"] == self.player_id:
                    self._parent.packet_queue.remove(p)
                    self._pos = p.data["position"]

    @property
    def player_id(self):
        return self._uid

    @player_id.setter
    def player_id(self, val):
        self._uid = val

    @property
    def is_local(self):
        return self._local

    @property
    def position(self):
        return self._pos

    @property
    def name(self):
        return self._name

    def __getstate__(self):
        return {"player_id": self.player_id, "name": self.name, "position": self.position}

    def __setstate__(self, attributes):
        self.__init__(attributes["position"], attributes["name"], False, attributes["player_id"], GAME_FACTORY["get_game"]())

    @name.setter
    def name(self, value):
        self._name = value

    @position.setter
    def position(self, value):
        self._pos = value

    def handle_packet(self, packet: Packet):
        if packet.packet_id == PACKETS.S2C_POSITION_UPDATE:
            if packet.data["player_id"] == self.player_id:
                self._pos = packet.data["position"]
