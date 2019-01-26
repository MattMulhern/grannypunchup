import logging
import sys
import pymunk
import pyxel
import settings

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Sprite:
    """ Base Sprite clas. """
    def __init__(self,
                 id, xpos, ypos,
                 imagebank, spritesheet_positions, attack_sprite_position, width, height, spritesheet_keycol,
                 mass, momentum, velocity):
        self.id = id
        self.xpos0 = xpos
        self.ypos0 = ypos
        self.imagebank = imagebank
        self.spritesheet_positions = spritesheet_positions
        self.width = width
        self.height = height
        self.spritesheet_keycol = spritesheet_keycol
        self.mass = mass
        self.momentum = momentum

        self.body = pymunk.Body(self.mass, self.momentum)
        self.body.sprite = self
        self.body.position = self.xpos0, self.ypos0
        self.body.velocity = velocity
        self.body.spriteid = id
        self.spritesheet_idx = 0
        self.attack_frames = 0
        self.attack_sprite_position = attack_sprite_position
        self.health = 100

    def die(self):
        """ for later animation use, should be overloaded """
        pass

    def is_attacking(self):
        if self.attack_frames > 0:
            return True
        return False

    def draw(self):
        if self.body.velocity != (0, 0):
            logger.debug("{0} at {1}, {2} travelling at {2}".format(self.id,
                                                                    self.body.position.x,
                                                                    self.body.position.y,
                                                                    self.body.velocity))
        if self.is_attacking():
            logger.debug(f"{self.id} is attacking [{self.attack_frames}]")
            self.attack_frames -= 1

        width = self.width
        if self.facing == 'left':
            width *= -1
        s_position = self.spritesheet_positions[self.spritesheet_idx]

        pyxel.blt((self.body.position.x - (self.width / 2)),
                  self.body.position.y - (self.height / 2),
                  self.imagebank,
                  s_position[0],
                  s_position[1],
                  width,
                  self.height,
                  self.spritesheet_keycol)


class Player(Sprite):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(48, 0), (48, 16)], attack_sprite_position=(48, 0), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        # spritesheet_ypos = spritesheet_ypos + ((player_num - 1) * height)
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 4), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'right'
        self.attack_length = settings.player_attack_length
        self.attack_power = settings.player_attack_power

    def update(self):
        num = self.player_num
        veldiff = 100
        if pyxel.frame_count % settings.sprite_anim_modulo == 0:
            if self.spritesheet_idx == (len(self.spritesheet_positions) - 1):
                self.spritesheet_idx = 0
            else:
                self.spritesheet_idx += 1

        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_UP")):
            self.body.apply_impulse_at_local_point((0, - veldiff), (0, 0))
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_DOWN")):
            self.body.apply_impulse_at_local_point((0, veldiff), (0, 0))
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_RIGHT")):
            self.facing = 'right'
            self.body.apply_impulse_at_local_point((veldiff, 0), (0, 0))
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_LEFT")):
            self.facing = 'left'
            self.body.apply_impulse_at_local_point((-veldiff, 0), (0, 0))
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_A")):
            logger.error(f"{self.id} attacking!")
            self.attack_frames += self.attack_length


class Enemy(Sprite):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(64, 64)], attack_sprite_position=(64, 64), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        # spritesheet_ypos = spritesheet_ypos + ((player_num - 1) * height)
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power

    def update(self):
        pass

    def handlepress(self, buttonName):
        if buttonName == 'up':
            self.body.apply_impulse_at_local_point((0, -10), (0, 0))
        elif buttonName == 'down':
            self.body.apply_impulse_at_local_point((0, 10), (0, 0))
        elif buttonName == 'right':
            self.body.apply_impulse_at_local_point((10, 0), (0, 0))
            self.facing = 'right'
        elif buttonName == 'left':
            self.body.apply_impulse_at_local_point((-10, 0), (0, 0))
            self.facing = 'left'
        elif buttonName == 'a':
            self.attack_frames += self.attack_length
        elif buttonName == 'b':
            self.useitem()
