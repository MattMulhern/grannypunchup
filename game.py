import pymunk
import logging
import sys
import pyxel
import settings
import csv

from sprites import Player, Enemy

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def resolve_player_collision(arbiter, space, data):
    sprite_a = arbiter.shapes[0].body.sprite
    sprite_b = arbiter.shapes[1].body.sprite
    # logger.debug(f"{sprite_a.id} is colliding with {sprite_b.id}")
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
        for line in lines:
            self.space.add(line)

        logger.info("game initialized.")
        self.players = {"Anna": Player("Anna", 50, 100,
                                       spritesheet_positions=[(0, 0)], velocity=(0, 0), player_num=1),
                        "Betrice": Player("Betrice", 10, 100,
                                          spritesheet_positions=[(0, 48)], velocity=(0, 0), player_num=2),
                        "Candice": Player("Candice", 100, 10,
                                          spritesheet_positions=[(0, 96)], velocity=(0, 0), player_num=3),
                        "Derp": Player("Derp", 100, 50,
                                       spritesheet_positions=[(0, 144)], velocity=(0, 0), player_num=4)}

        self.dead_grannys = []
        self.enemies = {}

        self.new_enemies = []

        for player in self.players.values():
            self.space.add(player.body, player.poly)

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
            if player.health <= 0:
                objs_to_kill.append(player)
        for enemy in self.enemies.values():
            enemy.update()
            if enemy.health <= 0:
                objs_to_kill.append(enemy)

        for obj in objs_to_kill:
            self.kill(obj)
        self.space.step(settings.space_dt)

    def draw(self):
        """ draw game to canvas """
        pyxel.text(10, 5, "Granny Punch Up", 14)
        pyxel.cls(0)
        self.draw_level()
        for player in self.players.values():
            player.draw()
        for enemy in self.enemies.values():
            enemy.draw()

    def handle_connect_event(self, sid, data):
        logger.debug(f"handling connect for {sid}")
        if len(self.enemies.keys()) > settings.max_enemies:
            logger.error('reached enemy limit, ignoring request')
        else:
            self.add_new_enemy(sid, data)

    def add_new_enemy(self, sid, data):
        newEnemy = Enemy(sid, 100, 50, velocity=(0, 0))
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
        obj.die()
        if isinstance(obj, Player):
            self.dead_grannys.append(obj)  # track player deaths
            del(self.players[obj.id])
        elif isinstance(obj, Enemy):
            del(self.enemies[obj.id])
        self.space.remove(obj.body)
