import logging
import sys
import pymunk
import pyxel
from sprite import Sprite
from pymunk import Vec2d


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Player(Sprite):
    """ test class """
    def __init__(self, id, xpos, ypos, imagebank=0, spritesheet_xpos=48, spritesheet_ypos=0, width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        spritesheet_ypos = spritesheet_ypos + ((player_num - 1) * height)
        print(spritesheet_xpos, spritesheet_ypos)
        super().__init__(id, xpos, ypos, imagebank, spritesheet_xpos, spritesheet_ypos, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.player_num = player_num

    def draw(self):
        if self.body.velocity != (0, 0):
            logger.debug("{0} at {1} travelling at {2}".format(self.id, self.body.position, self.body.velocity))

        pyxel.blt((self.body.position.x - (self.width / 2)),
                  self.body.position.y - (self.height / 2),
                  self.imagebank,
                  self.spritesheet_xpos,
                  self.spritesheet_ypos,
                  self.width,
                  self.height,
                  self.spritesheet_keycol)

    def update(self):
        num = self.player_num
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_UP")):
            self.body.apply_impulse_at_local_point((0, -10), (0, 0))
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_DOWN")):
            self.body.apply_impulse_at_local_point((0, 10), (0, 0))
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_RIGHT")):
            self.body.apply_impulse_at_local_point((10, 0), (0, 0))
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_LEFT")):
            self.body.apply_impulse_at_local_point((-10, 0), (0, 0))
        if pyxel.btnr(getattr(pyxel, f"GAMEPAD_{num}_UP")) and pyxel.btnr(getattr(pyxel, f"GAMEPAD_{num}_DOWN")) and pyxel.btnr(getattr(pyxel, f"GAMEPAD_{num}_RIGHT")) and pyxel.btnr(getattr(pyxel, f"GAMEPAD_{num}_LEFT")):
            print('Released')
            # self.body.velocity(0, 0)
