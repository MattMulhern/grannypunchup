import pymunk
import logging
import sys
import pyxel
import settings
from sprites import Player, Enemy

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Game:
    """ Class used for game """
    def __init__(self):
        pyxel.image(0).load(0, 0, "assets/villagers.png")
        self.space = self._init_space()
        logger.info("game initialized.")
        self.players = [Player("Anna", 50, 50, velocity=(0, 0), player_num=1),
                        Player("Betrice", 50, 50, velocity=(0, 0), player_num=2),
                        Player("Candice", 50, 50, velocity=(0, 0), player_num=3),
                        Player("Derp", 50, 50, velocity=(0, 0), player_num=4)]
            
        # self.enemies = [Enemy("Adolf", 100, 50, velocity=(0, 0)),
        #                 Enemy("Jean Claude Grand Ma", 100, 50, velocity=(0, 0)),
        #                 Enemy("Cunt ripper", 100, 50, velocity=(0, 0)),
        #                 Enemy("Dick cheese", 100, 50, velocity=(0, 0))]
        self.enemies = {}

        pyxel.tilemap(0).set(
            0, 0, ["0202020401006061620040", "4203202122030001020360", "0202020401006061620040"], 0
        )

        for player in self.players:
            self.phys.add(player.body, player.poly)

    def _init_space(self):
        """ gravity, canvas etc """
        self.phys = pymunk.Space()

    def update(self):
        """ update game objects """
        # print(self.space.bodies)
        for player in self.players:
            player.update()
        # for enemy in self.enemies.values():
        #     enemy.update()
        self.phys.step(settings.phys_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        for player in self.players:
            player.draw()
        for enemy in self.enemies.values():
            enemy.draw()
        # pyxel.bltm(0, 0, 0, 0, 0, 100, 100, 0)
    
    def handle_connect_event(self, sid, data):
        if len(self.enemies.keys()) > settings.max_enemies:
            logger.error('reached enemy limit, ignoring request')
        else:
            self.add_new_enemy(sid, data)

    def add_new_enemy(self, sid, data):
        newEnemy = Enemy("Network Adolf", 100, 50, velocity=(0, 0))
        self.enemies[sid] = newEnemy
        self.phys.add(newEnemy.body,  newEnemy.poly)

    def handle_press_event(self, sid, buttonName):
        if sid not in self.enemies.keys():
            logger.error(f"unrecognised press event from {sid}, ignoring")
            return
        self.enemies[sid].handlepress(buttonName)

    def handle_release_event(self, sid, data):
        pass
