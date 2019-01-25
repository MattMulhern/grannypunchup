import pymunk
import logging
import sys
import pyxel
import settings
from sprites import Player

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

        for player in self.players:
            self.phys.add(player.body, player.poly)

    def _init_space(self):
        """ gravity, canvas etc """
        self.phys = pymunk.Space()

    def update(self):
        """ update game objects """
        self.phys.step(settings.phys_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        for player in self.players:
            player.draw()
