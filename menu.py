import logging
import sys
import pyxel

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Menu:
    """ Class used for game """
    def __init__(self):
        logger.info("menu initialized.")

    def update(self):
        logger.debug("menu.update()")
        pass

    def draw(self):
        """ draw title to canvas """
        pyxel.text(10, 5, "menu", 14)
