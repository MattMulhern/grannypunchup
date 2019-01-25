import logging
import sys
import pymunk

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Sprite:
    """ Base Sprite clas. """
    def __init__(self,
                 id, xpos, ypos,
                 imagebank, spritesheet_xpos, spritesheet_ypos, width, height, spritesheet_keycol,
                 mass, momentum, velocity):
        self.id = id
        self.xpos0 = xpos
        self.ypos0 = ypos
        self.imagebank = imagebank
        self.spritesheet_xpos = spritesheet_xpos
        self.spritesheet_ypos = spritesheet_ypos
        self.width = width
        self.height = height
        self.spritesheet_keycol = spritesheet_keycol
        self.mass = mass
        self.momentum = momentum

        self.body = pymunk.Body(self.mass, self.momentum)
        self.body.position = self.xpos0, self.ypos0
        self.body.velocity = velocity
