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
        self.enemies = [Enemy("Adolf", 100, 50, velocity=(0, 0)),
                        Enemy("Jean Claude Grand Ma", 100, 50, velocity=(0, 0)),
                        Enemy("Cunt ripper", 100, 50, velocity=(0, 0)),
                        Enemy("Dick cheese", 100, 50, velocity=(0, 0))]
        pyxel.tilemap(0).set(
            0, 0, ["0202020401006061620040", "4203202122030001020360", "0202020401006061620040"], 0
        )

        for player in self.players:
            self.phys.add(player.body, player.poly)
        for enemy in self.enemies:
            self.phys.add(enemy.body, enemy.poly)

    def _init_space(self):
        """ gravity, canvas etc """
        self.phys = pymunk.Space()

    def update(self):
        """ update game objects """
        for player in self.players:
            player.update()
        for enemy in self.enemies:
            enemy.update()
        self.phys.step(settings.phys_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        for player in self.players:
            player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pyxel.bltm(0, 0, 0, 0, 0, 100, 100, 0)
