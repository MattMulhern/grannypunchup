import pymunk
import logging
import sys
import pyxel
import settings
import csv
import random

from sprites import Player, Enemy, Baby, Girl, Woman, Pregnant, Boy, Man, Granda

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def resolve_player_collision(arbiter, space, data):
    if isinstance(arbiter.shapes[0], pymunk.Segment):
        arbiter.shapes[1].body.sprite.health -= settings.det_wall_dmg
        return
    if isinstance(arbiter.shapes[1], pymunk.Segment):
        arbiter.shapes[0].body.sprite.health -= settings.det_wall_dmg
        return
    sprite_a = arbiter.shapes[0].body.sprite
    sprite_b = arbiter.shapes[1].body.sprite

    if sprite_a.death_frames > 0 or sprite_b.death_frames > 0:
        return
    if sprite_a.dead or sprite_b.dead:
        return

    if sprite_a.is_attacking():
        logger.info(f"{sprite_a.id} hit {sprite_b.id} for {sprite_a.attack_power}, {sprite_b.health} left")
        sprite_b.health -= sprite_a.attack_power
    if sprite_b.is_attacking():
        logger.info(f"{sprite_b.id} hit {sprite_a.id} for {sprite_b.attack_power}, {sprite_a.health} left")
        sprite_a.health -= sprite_b.attack_power


class Game:
    """ Class used for game """

    def __init__(self, fps=1):
        pyxel.image(0).load(0, 0, "assets/villagers-export.png")
        pyxel.image(1).load(0, 0, "assets/16X16-export.png")
        self._init_space()
        lines = []
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        for x in [z for z in range(0, 41)] + [z for z in range(158, 166)]:
            lines.append(pymunk.Segment(body, (0, x), (255, x), 30))
        lines.append(pymunk.Segment(body, (-25, 0), (-25, 144), 30))
        lines.append(pymunk.Segment(body, (265, 0), (265, 144), 30))
        for line in lines:
            self.space.add(line)
        death_wall = Enemy(0, xpos=0, ypos=0, imagebank=0,
                           spritesheet_positions=[(3, 57)], attack_sprite_position=(0, 0), width=1,
                           height=settings.canvas_y, spritesheet_keycol=0, mass=100, momentum=1, velocity=(0, 0),
                           player_num=1)
        death_wall.attack_frames = pymunk.inf
        death_wall.health = pymunk.inf
        death_wall.poly = pymunk.Segment(body, (0, 0), (0, 144), 10)
        death_wall.poly.collision_type = 1
        death_wall.body = pymunk.Segment(body, (0, 0), (0, 144), 10)
        death_wall.body.sprite = death_wall
        self.space.add(death_wall.body, death_wall.poly)

        logger.info("game initialized.")
        start_y = 50
        self.players = {"Anna": Player("Anna", 53, start_y,
                                       spritesheet_positions=[(0, 0)], velocity=(0, 0), player_num=1),
                        "Betrice": Player("Betrice", 63, start_y,
                                          spritesheet_positions=[(0, 48)], velocity=(0, 0), player_num=2),
                        "Candice": Player("Candice", 110, start_y,
                                          spritesheet_positions=[(0, 96)], velocity=(0, 0), player_num=3),
                        "Derp": Player("Derp", 115, start_y,
                                       spritesheet_positions=[(0, 144)], velocity=(0, 0), player_num=4)}

        self.dead_grannys = []
        self.enemies = {}

        self.new_enemies = []

        for player in self.players.values():
            self.space.add(player.body, player.poly)

        self.boss_fight = False
        self.boss_dead = False

    def _init_space(self):
        """ gravity, canvas etc """
        self.space = pymunk.Space(threaded=True)
        self.space.damping = settings.space_damping
        self.colhandler = self.space.add_collision_handler(1, 1)
        self.colhandler.post_solve = resolve_player_collision
        self.space.damping = settings.space_damping

    def reset(self):
        objs_to_kill = []
        for player in self.players.values():
            objs_to_kill.append(player)
        for enemy in self.enemies.values():
            objs_to_kill.append(enemy)

        for obj in objs_to_kill:
            self.kill(obj)
        self.dead_grannys = []
        pyxel.frame_count = 0
        self.__init__()

    def draw_csv(self, csv_file, offset):
        if offset >= 512 - 32:
            offset = 512 - 32
            self.boss_fight = True

        with open(csv_file) as csv_map:
            csv_reader = csv.reader(csv_map, delimiter=',')
            y_pos = 0
            for row in csv_reader:
                x_pos = 0
                for value in row[0 + offset:32 + offset]:
                    y = (int(value) // 32)
                    x = (int(value) % 32)
                    pyxel.blt(x_pos, y_pos, 1, x * 8, y * 8, 8, 8, 0)
                    x_pos += 8
                y_pos += 8

    def draw_level(self):
        offset = pyxel.frame_count // settings.scrollspeed
        self.draw_csv('assets/Level_floor.csv', offset)
        self.draw_csv('assets/Level_walls.csv', offset)
        self.draw_csv('assets/Level_carpet.csv', offset)
        self.draw_csv('assets/Level_objects.csv', offset)

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            logger.info("Exit.")
            # pyxel.quit()
            self.reset()

        self.flushingEnemies = True
        enemies = self.new_enemies
        self.new_enemies = []
        self.flushingEnemies = False

        for (sid, newEnemy) in enemies:
            self.enemies[sid] = newEnemy
            self.space.add(newEnemy.body,  newEnemy.poly)
        """ update game objects """
        objs_to_kill = []
        for player in self.players.values():
            player.update()
            if player.dead:
                logger.debug(f"{player.id} is dead!")
                objs_to_kill.append(player)
            elif player.death_frames > 0:
                logger.debug(f"{player.id} is dying! {player.death_frames}")
                player.death_frames -= 1
                if player.death_frames <= 0:
                    logger.debug(f"{player.id} TRUE DEATH! {player.death_frames}")
                    player.dead = True
            elif player.health <= 0:
                player.death_frames = settings.death_duration
        for enemy in self.enemies.values():
            enemy.update()
            if enemy.dead:
                logger.debug(f"{enemy.id} is dead!")
                objs_to_kill.append(enemy)
            elif enemy.death_frames > 0:
                logger.debug(f"{enemy.id} is dying! {enemy.death_frames}")
                enemy.death_frames -= 1
                if enemy.death_frames <= 0:
                    logger.debug(f"{enemy.id} TRUE DEATH! {enemy.death_frames}")
                    enemy.dead = True
            elif enemy.health <= 0:
                enemy.death_frames = settings.death_duration

        for obj in objs_to_kill:
            self.kill(obj)

        self.space.step(settings.space_dt)
        logger.debug(f"BODIES:{self.space.bodies}")

        if len(self.enemies) < settings.required_enemies:
            pyxel.frame_count = 0

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        pyxel.cls(0)
        self.draw_level()
        for player in self.players.values():
            player.draw()
        for enemy in self.enemies.values():
            enemy.draw()
        """ GRANDAS  below """

        granda_x = -6
        pyxel.blt(granda_x, 46, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 56, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 66, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 76, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 86, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 96, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 106, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 116, 0, 112, 64, 16, 16, 0)
        pyxel.blt(granda_x, 126, 0, 112, 64, 16, 16, 0)

    def handle_disconnect_event(self, sid):
        if sid in self.enemies.keys():
            self.kill(self.enemies[sid])

    def handle_connect_event(self, sid, data):
        logger.debug(f"handling connect for {sid}")
        if len(self.enemies.keys()) > settings.max_enemies:
            logger.error('reached enemy limit, ignoring request')
        else:
            self.add_new_enemy(sid, data)

    def add_new_enemy(self, sid, data):
        class_list = ["Baby", "Girl", "Woman", "Pregnant", "Boy", "Man", "Granda"]
        enemy_class = random.choice(class_list)
        if enemy_class == "Player":
            newEnemy = Player(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Enemy":
            newEnemy = Enemy(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Baby":
            newEnemy = Baby(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Girl":
            newEnemy = Girl(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Woman":
            newEnemy = Woman(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Pregnant":
            newEnemy = Pregnant(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Boy":
            newEnemy = Boy(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Man":
            newEnemy = Man(sid, 100, 50, velocity=(0, 0))
        elif enemy_class == "Granda":
            newEnemy = Granda(sid, 100, 50, velocity=(0, 0))
        else:
            logger.error(f"add_new_enemy: could not find class {enemy_class}")
            return False

        # self.enemies[sid] = data
        while self.flushingEnemies:
            pass
        self.new_enemies.append((sid, newEnemy))

    def handle_press_event(self, sid, buttonName):
        if sid not in self.enemies.keys():
            logger.error(f"unrecognised press event from {sid}, ignoring")
            return
        self.enemies[sid].handlepress(buttonName)

    def handle_release_event(self, sid, buttonName):
        if sid not in self.enemies.keys():
            logger.error(f"unrecognised release event from {sid}, ignoring")
            return
        self.enemies[sid].handlerelease(buttonName)

    def kill(self, obj):
        logger.debug(f"game killing {obj.id}")
        obj.die()
        if isinstance(obj, Player):
            self.dead_grannys.append(obj)  # track player deaths
            del(self.players[obj.id])
        elif isinstance(obj, Enemy):
            del(self.enemies[obj.id])
        self.space.remove(obj.body)
