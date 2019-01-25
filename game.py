import pymunk
import logging
import sys
import pyxel
import settings

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Game:
    """ Class used for game """
    def __init__(self):
        self.space = self._init_space()
        logger.info("game initialized.")

    def _init_space(self):
        """ gravity, canvas etc """
        self.phys = pymunk.Space()

    def update(self):
        """ update game objects """
        self.phys.step(settings.phys_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "game", 14)
