import logging
import sys
import pymunk
import pyxel
import random
import settings

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Sprite:
    """ Base Sprite clas. """
    def __init__(self,
                 id, xpos, ypos,
                 imagebank, spritesheet_positions, attack_sprite_position, width, height, spritesheet_keycol,
                 mass, momentum, velocity, max_health):
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
        self.max_health = max_health
        self.health = max_health
        self.equipped = 'nothing'
        self.death_frames = 0
        self.dead = False
    def die(self):
        """ for later animation use, should be overloaded """
        pass

    def is_attacking(self):
        if self.attack_frames > 0:
            return True
        return False

    def draw(self):
        if self.dead:
            return  # to be deleted in next frame

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

        if self.death_frames > 0:
            logger.debug(f"dead drawing {self.id}: {self.death_frames}: {self.dead}")
            pyxel.blt(self.body.position.x,
                      self.body.position.y,
                      self.imagebank,
                      s_position[0],
                      s_position[1],
                      width,
                      -self.height,
                      self.spritesheet_keycol)

            return
        if self.is_attacking():
            logger.debug(f"drawing attack frame for {self.id}")
            s_position = (self.attack_sprite_position[0], self.attack_sprite_position[1])
            
        pyxel.blt(self.body.position.x,
                  self.body.position.y,
                  self.imagebank,
                  s_position[0],
                  s_position[1],
                  width,
                  self.height,
                  self.spritesheet_keycol)

        if (self.health / self.max_health) > 0.7:
            rect_col = 11
        elif (self.health / self.max_health) > 0.4:
            rect_col = 9
        else:
            rect_col = 8

        pyxel.rect(self.body.position.x,
                   self.body.position.y - 1,
                   self.body.position.x + ((self.width / self.max_health) * self.health),
                   self.body.position.y,
                   rect_col)

    def useitem(self):
        logger.info(f"{self.id} uses {self.equipped}!")


class Player(Sprite):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(0, 0)], attack_sprite_position=(0, 0), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1, max_health=settings.player_max_health):

        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity, max_health)

        self.poly = pymunk.Circle(self.body, (self.width / 4), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'right'
        self.attack_length = settings.player_attack_length
        self.attack_power = settings.player_attack_power
        self.veldiff = settings.player_veldiff

        dpos_x = self.spritesheet_positions[0][0] + self.width  # TODO: fix for where they really are!
        dpos_y = self.spritesheet_positions[0][1]  # TODO: fix for where they really are!

        # add 2nd walking animation
        walk_anim_2_y = self.spritesheet_positions[0][1] + self.height
        walk_anim_2_x = self.spritesheet_positions[0][0]
        self.spritesheet_positions.append((walk_anim_2_x, walk_anim_2_y))

        attack_anim_x = self.spritesheet_positions[0][0]
        attack_anim_y = self.spritesheet_positions[0][1] + (self.height * 2)
        self.attack_sprite_position = (attack_anim_x, attack_anim_y)

    def update(self, boss_dead):
        num = self.player_num
        if pyxel.frame_count % settings.sprite_anim_modulo == 0:
            if self.spritesheet_idx == (len(self.spritesheet_positions) - 1):
                self.spritesheet_idx = 0
            else:
                self.spritesheet_idx += 1

        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_UP")):
            self.body.apply_impulse_at_local_point((0, - self.veldiff), (0, 0))
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_DOWN")):
            self.body.apply_impulse_at_local_point((0, self.veldiff), (0, 0))
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_RIGHT")) or boss_dead:
            self.facing = 'right'
            self.body.apply_impulse_at_local_point((self.veldiff, 0), (0, 0))
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_LEFT")):
            self.facing = 'left'
            self.body.apply_impulse_at_local_point((-self.veldiff, 0), (0, 0))
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_A")):
            self.attack_frames = self.attack_length
        if pyxel.btn(pyxel.KEY_B) or pyxel.btn(getattr(pyxel, f"GAMEPAD_{num}_B")):
            self.useitem()


class Enemy(Sprite):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(64, 64)], attack_sprite_position=(64, 64), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1, max_health=100):
        # spritesheet_ypos = spritesheet_ypos + ((player_num - 1) * height)
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity, max_health)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff
        if not isinstance(self, Boss):
            self.spritesheet_positions = [(spritesheet_positions[0][0],
                                           random.randrange(0, 6) * 32)]
        else:
            self.spritesheet_positions = [(128, 0)]

        # add 2nd walking animation
        walk_anim_2_y = self.spritesheet_positions[0][1] + self.height
        walk_anim_2_x = self.spritesheet_positions[0][0]
        self.spritesheet_positions.append((walk_anim_2_x, walk_anim_2_y))

        dpos_x = self.spritesheet_positions[0][0] + self.width  # TODO: fix for where they really are!
        dpos_y = self.spritesheet_positions[0][1]  # TODO: fix for where they really are!

        self.attack_sprite_position = self.spritesheet_positions[0]
    def update(self):
        if pyxel.frame_count % settings.sprite_anim_modulo == 0:
            if self.spritesheet_idx == (len(self.spritesheet_positions) - 1):
                self.spritesheet_idx = 0
            else:
                self.spritesheet_idx += 1
        if self.btn_ctx['up']:
            self.body.apply_impulse_at_local_point((0, -self.veldiff), (0, 0))
        if self.btn_ctx['down']:
            self.body.apply_impulse_at_local_point((0, self.veldiff), (0, 0))
        if self.btn_ctx['right']:
            self.body.apply_impulse_at_local_point((self.veldiff, 0), (0, 0))
        if self.btn_ctx['left']:
            self.body.apply_impulse_at_local_point((-self.veldiff, 0), (0, 0))

    def handlepress(self, buttonName):
        if buttonName == 'up':
            self.btn_ctx['up'] = True
        elif buttonName == 'down':
            self.btn_ctx['down'] = True
        elif buttonName == 'right':
            self.btn_ctx['right'] = True
            self.facing = 'right'
        elif buttonName == 'left':
            self.btn_ctx['left'] = True
            self.facing = 'left'
        elif buttonName == 'a':
            self.attack_frames = self.attack_length
        elif buttonName == 'b':
            self.useitem()

    def handlerelease(self, buttonName):
        if buttonName == 'up':
            self.btn_ctx['up'] = False
        elif buttonName == 'down':
            self.btn_ctx['down'] = False
        elif buttonName == 'right':
            self.btn_ctx['right'] = False
            self.facing = 'right'
        elif buttonName == 'left':
            self.btn_ctx['left'] = False
            self.facing = 'left'


class Baby(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(48, 32)], attack_sprite_position=(128, 64), width=16,
                 height=16, spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power - 3
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 120


class Girl(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(16, 64)], attack_sprite_position=(128, 32), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 70


class Woman(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(32, 64)], attack_sprite_position=(128, 48), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power + 2
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 70


class Pregnant(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(64, 64)], attack_sprite_position=(128, 80), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power + 5
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff - 30


class Boy(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(80, 64)], attack_sprite_position=(128, 96), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power - 1
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 100


class Man(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(96, 64)], attack_sprite_position=(128, 112), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power + 3
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 50


class Granda(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(112, 64)], attack_sprite_position=(128, 128), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.enemy_attack_power + 3
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 50


class Boss(Enemy):
    """ Gamepad player class """
    def __init__(self, id, xpos, ypos, imagebank=0,
                 spritesheet_positions=[(128, 0)], attack_sprite_position=(64, 64), width=16, height=16,
                 spritesheet_keycol=0, mass=1, momentum=1, velocity=(0, 0), player_num=1):
        super().__init__(id, xpos, ypos, imagebank, spritesheet_positions, attack_sprite_position, width, height,
                         spritesheet_keycol, mass, momentum, velocity, max_health=settings.boss_max_health)

        self.poly = pymunk.Circle(self.body, (self.width / 2), offset=(0, 0))
        self.poly.collision_type = 1
        self.player_num = player_num
        self.facing = 'left'
        self.attack_power = settings.boss_attack_power
        self.attack_length = settings.enemy_attack_length
        self.btn_ctx = {'up': False, 'down': False, 'left': False, 'right': False, 'a': False, 'b': False}
        self.veldiff = settings.enemy_veldiff + 150
        self.attack_frames = pymunk.inf
