import pygame as pg
from .network.server import Server
from .network.client import Client
from .network.inetwork import INetwork
from .network.packet import PACKETS, Packet
from .network.packets import S2CPositionUpdate, S2CFullUpdate, S2CHello
from .player import Player
from collections import deque
from sys import argv, exit
from .utils.game_factory import GAME_FACTORY

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS_TIMER_ID = 69
FPS_TIMER_DELAY = int(1000 / 60)


class Game:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    surface = None
    running = False
    is_server = False
    network: INetwork = None
    server: Server = None
    client: Client = None
    packet_queue: deque = deque()
    players = []
    player: Player = None

    def init(self, is_server: bool):
        GAME_FACTORY["get_game"] = lambda: self
        self.is_server = is_server
        if is_server:
            network = Server("127.0.0.1", 12345)
            network.on_packet(self.on_packet)
            self.server = network
            self.network = network
        else:
            network = Client("127.0.0.1", 12345)
            network.on_packet(lambda packet: self.on_packet(network, packet))
            self.client = network
            self.network = network

        self.network.create()
        self.network.run(self.on_startup)

        if not self.is_server:
            self.player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), "player", True, 0, self)
            self.players.append(self.player)
        if not self.is_server:
            pg.init()
            pg.display.set_caption("game")

            self.surface = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True

        if not self.is_server:
            pg.time.set_timer(FPS_TIMER_ID, FPS_TIMER_DELAY)

        while self.running:
            self.tick()
            if not self.is_server:

                for ev in pg.event.get():
                    if ev.type == pg.QUIT:
                        self.running = False
                    elif ev.type == FPS_TIMER_ID:
                        self.surface.fill((0, 0, 0))
                        self.draw()
                        pg.display.flip()
                    else:
                        self.on_event(ev)

        # CLEANUP SHIT

    def tick(self):
        for player in self.players:
            player.tick()

    def draw(self):
        for player in self.players:
            player.draw(self.surface)

    def on_event(self, event: pg.event.Event):
        ...

    def on_startup(self, error: (Exception | None)):
        if error is not None:
            print("Failed to startup game. Error: " + str(error))
        else:
            print(f"Successfully started network {'server' if self.is_server else 'client'}.")

    def on_packet(self, client, packet: Packet):
        if packet.packet_id == PACKETS.C2S_POSITION_UPDATE:
            self.server.broadcast(S2CPositionUpdate(packet.data['player_id'], packet.data['position']))
        elif packet.packet_id == PACKETS.C2S_HELLO:
            print(f"Hello packet received")
            next_player_id = (max(self.players, key=lambda p: p.player_id)).player_id + 1 if len(self.players) > 0 else 1
            new_player = Player((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), "player", False, next_player_id, self)
            self.players.append(new_player)
            client.send_packet(S2CHello(next_player_id))
            self.server.broadcast(S2CFullUpdate(self.players))
        elif packet.packet_id == PACKETS.S2C_POSITION_UPDATE:
            for player in self.players:
                if player.player_id == packet.data['player_id']:
                    player.handle_packet(packet)
                    break
        elif packet.packet_id == PACKETS.S2C_HELLO:
            self.player.player_id = packet.data['your_player_id']
        elif packet.packet_id == PACKETS.S2C_FULL_UPDATE:
            for player in packet.data["players"]:
                if self.get_player(player.player_id) is None:
                    self.players.append(player)

    def get_player(self, pid):
        for player in self.players:
            if player.player_id == pid:
                return player
        return None


def run():
    mode = "client"
    if len(argv) == 2:
        if argv[1] == "server":
            mode = "server"
        elif argv[1] == "client":
            mode = "client"
        else:
            print("Error: invalid mode")
            exit(1)
    print(f"Running as {mode.capitalize()}")
    Game().init(is_server=(mode == "server"))
