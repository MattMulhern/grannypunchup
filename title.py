import logging
import sys
import pyxel

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Title:
    """ Class used for game """
    def __init__(self):
        logger.info("title initialized.")
        pyxel.image(2).load(0, 0, "assets/Title-export.png")

    def update(self):
        # logger.debug("title.update()")
        pass

    def draw(self):
        """ draw title to canvas """
        pyxel.blt(0, 0, 2, 0, 0, 255, 128, 0)
