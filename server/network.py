import json
import socket
import string
import random
from threading import Lock, Thread

from server.utils import layout_ships

lock = Lock()


class Room:
    def __init__(self):
        self.players = []
        self.sent_board = False
        self._id = ""

    def send_board(self):
        self.players[0].turn = random.choice((True, False))
        self.players[1].turn = not self.players[0].turn
        self.players[0].layout, self.players[1].layout = layout_ships(), layout_ships()
        self.players[0].opponent, self.players[1].opponent = (
            self.players[1],
            self.players[0],
        )
        for player in self.players:
            player.conn.send(
                {
                    "category": "BOARD",
                    "payload": [
                        player.turn,
                        player.layout,
                        [
                            (xi, yi, square["ship"])
                            for xi, x in enumerate(player.opponent.layout)
                            for yi, square in enumerate(x)
                            if square["ship"]
                        ],
                    ],
                }
            )


class ServerPlayer:
    def __init__(self, conn, room=None):
        self.conn = conn
        self.room = room


class Network:
    server_addr = ""
    port = 1234
    address = server_addr, port

    def __init__(
        self, sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM), is_server=True
    ):
        self.server = sock
        if is_server:
            self.game_list = {}
            self.server.bind(self.address)
            self.wait_for_connection()

    def wait_for_connection(self):
        self.server.listen()
        while True:
            conn, address = self.server.accept()
            print("Connected to: ", address)

            conn = Network(sock=conn, is_server=False)
            # if len(self.game_list[-1].players) >= 2:
            #     self.game_list.append(Room())
            # self.game_list[-1].players.append(
            #     (p := ServerPlayer(conn, self.game_list[-1]))
            # )
            lock.acquire()
            Thread(
                target=self.proceed_with_connection,
                args=(ServerPlayer(conn),),
            ).start()
            lock.release()
            print(self.game_list)
            # for game in self.game_list:
            #     if not game.sent_board:
            #         if len(game.players) == 2:
            #             game.send_board()
            #             game.sent_board = True

    def proceed_with_connection(self, player):
        while True:
            try:
                data = player.conn.receive()
                if not data:
                    break
                if data["category"] == "OVER":
                    if player.room and player.room._id in self.game_list:
                        del self.game_list[player.room._id]
                    player.room = None
                elif data["category"] == "CREATE":
                    i = self.generate_id()
                    self.game_list[i] = Room()
                    self.game_list[i]._id = i
                    self.game_list[i].players.append(player)
                    player.room = self.game_list[i]
                    player.conn.send({"category": "ID", "payload": i})
                elif data["category"] == "JOIN":
                    try:
                        if len(self.game_list[data["payload"]].players) == 2:
                            player.conn.send("TAKEN")
                        else:
                            player.room = self.game_list[data["payload"]]
                            self.game_list[data["payload"]].players.append(player)
                            self.game_list[data["payload"]].send_board()
                    except KeyError:
                        player.conn.send("INVALID")
                elif data["category"] == "POSITION":
                    player.opponent.conn.send(data)
            except:
                break
        try:
            player.opponent.conn.send("END")
        except AttributeError:
            print("Closed Without Pair")
        if player.room and player.room._id in self.game_list:
            del self.game_list[player.room._id]
        player.conn.close()
        return

    def receive(self):
        buff = b""
        n = int.from_bytes(self.server.recv(4)[:4], "big")
        while n > 0:
            b = self.server.recv(n)
            buff += b
            n -= len(b)
        return json.loads(buff.decode())

    def send(self, *data):
        if len(data) == 1:
            data = data[0]
        final_data = b""
        data = json.dumps(data)
        final_data += len(data).to_bytes(4, "big")
        final_data += data.encode()
        try:
            self.server.send(final_data)
        except:
            pass

    def close(self):
        self.server.close()

    def generate_id(self):
        _id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        while _id in self.game_list.keys():
            _id = "".join(random.choice(string.ascii_lowercase) for _ in range(6))
        return _id
