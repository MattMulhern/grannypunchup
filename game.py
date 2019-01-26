import pymunk
import logging
import sys
import pyxel
import settings
import csv

from sprites import Player, Enemy

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Game:
    """ Class used for game """

    def __init__(self):
        pyxel.image(0).load(0, 0, "assets/villagers.png")
        pyxel.image(1).load(0, 0, "assets/16X16-export.png")
        self.space = self._init_space()
        logger.info("game initialized.")
        self.players = {"Anna": Player("Anna", 50, 50, velocity=(0, 0), player_num=1),
                        "Betrice": Player("Betrice", 50, 50, velocity=(0, 0), player_num=2),
                        "Candice": Player("Candice", 50, 50, velocity=(0, 0), player_num=3),
                        "Derp": Player("Derp", 50, 50, velocity=(0, 0), player_num=4)}
        self.enemies = {}

        self.new_enemies = []

        pyxel.tilemap(0).set(
            0, 0, ["0202020401006061620040",
                   "4203202122030001020360", "0202020401006061620040"], 0
        )

        for player in self.players.values():
            self.phys.add(player.body, player.poly)

    def _init_space(self):
        """ gravity, canvas etc """
        self.phys = pymunk.Space()
        self.phys.damping = settings.space_damping
        self.phys.add_collision_handler(1, 1)

    def resolve_attack(space, arbiter):
        print("resolve attack!")

    def draw_level(self):
        with open('assets/Level.csv') as csv_map:
            csv_reader = csv.reader(csv_map, delimiter=',')
            y_pos = 0
            for row in csv_reader:
                x_pos = 0
                for value in row[0:32]:
                    y = (int(value) // 32)
                    x = (int(value) % 32)
                    pyxel.blt(x_pos, y_pos, 1, x * 8, y * 8, 8, 8, 14)
                    x_pos += 8
                y_pos += 8

    def update(self):
        self.flushingEnemies = True
        enemies = self.new_enemies
        self.new_enemies = []
        self.flushingEnemies = False

        for (sid, newEnemy) in enemies:
            self.enemies[sid] = newEnemy
            self.phys.add(newEnemy.body,  newEnemy.poly)
        """ update game objects """
        for player in self.players.values():
            player.update()
        for enemy in self.enemies.values():
            enemy.update()
        self.phys.step(settings.phys_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        self.draw_level()
        for player in self.players.values():
            player.draw()
        for enemy in self.enemies.values():
            enemy.draw()

    def handle_connect_event(self, sid, data):
        if len(self.enemies.keys()) > settings.max_enemies:
            logger.error('reached enemy limit, ignoring request')
        else:
            self.add_new_enemy(sid, data)

    def add_new_enemy(self, sid, data):
        newEnemy = Enemy("Network Adolf", 100, 50, velocity=(0, 0))
        # self.enemies[sid] = data
        while self.flushingEnemies:
            pass
        self.new_enemies.append((sid, newEnemy))

    def handle_press_event(self, sid, buttonName):
        if sid not in self.enemies.keys():
            logger.error(f"unrecognised press event from {sid}, ignoring")
            return
        self.enemies[sid].handlepress(buttonName)

    def handle_release_event(self, sid, data):
        pass

    def kill(self, obj):
        obj.die()
        if isinstance(obj, Player):
            del(self.players[obj.id])
        elif isinstance(obj, Enemy):
            del(self.enemies[obj.id])
        self.phys.remove(obj.body)
