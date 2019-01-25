import pyxel
import sys
import logging

import game
import title
import menu
import settings

logger = logging.getLogger("main")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

PALETTE = pyxel.DEFAULT_PALETTE


class App:
    """ main class used for globals e.g. threading etc """
    def __init__(self):
        self.ctx = {"cur_frame": settings.starting_frame}
        pyxel.init(settings.canvas_x, settings.canvas_y, palette=PALETTE, scale=settings.scale)

        # initialize all frames
        self.title = title.Title()
        self.menu = menu.Menu()
        self.game = game.Game()
        logger.info("App initialized")

    def run(self):
        pyxel.run(app.update, app.draw)

    def update(self):
        """ checks for quit signal, then calls update() for current frame """
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            logger.info("Exit.")
            sys.exit(0)

        """ DEBUG """
        if pyxel.btnp(pyxel.KEY_T):
            self.ctx['cur_frame'] = 'title'
        if pyxel.btnp(pyxel.KEY_G):
            self.ctx['cur_frame'] = 'game'
        if pyxel.btnp(pyxel.KEY_M):
            self.ctx['cur_frame'] = 'menu'
        if pyxel.btnp(pyxel.GAMEPAD_1_A):
            logger.debug("A PRESSED!")
        """ END DEBUG """

        if self.ctx['cur_frame'] == 'game':
            self.game.update()
        elif self.ctx['cur_frame'] == 'menu':
            self.menu.update()
        elif self.ctx['cur_frame'] == 'title':
            self.title.update()
        else:
            logging.error('invalid context frame %s' % self.ctx['cur_frame'])
            sys.exit(1)

    def draw(self):
        """ Calls draw() for current frame """
        pyxel.cls(0)
        if self.ctx['cur_frame'] == 'game':
            self.game.draw()
        elif self.ctx['cur_frame'] == 'menu':
            self.menu.draw()
        elif self.ctx['cur_frame'] == 'title':
            self.title.draw()
        else:
            logging.error('invalid context frame %s' % self.ctx['cur_frame'])
            sys.exit(1)


if __name__ == '__main__':
    app = App()
    app.run()
