import pyxel
import sys
import logging
import asyncio
import threading
from aiohttp import web
import socketio


import game
import title
import menu
import settings

logger = logging.getLogger("main")
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

PALETTE = pyxel.DEFAULT_PALETTE
sio = socketio.AsyncServer()
loop = asyncio.get_event_loop()


class App:
    """ main class used for globals e.g. threading etc """

    def __init__(self):
        self.ctx = {"cur_frame": settings.starting_frame}
        pyxel.init(settings.canvas_x, settings.canvas_y,
                   palette=PALETTE, scale=settings.scale)

        pyxel.load('assets/granny.pyxel')
        pyxel.play(0, [0, 1], loop=True)

        # initialize all frames
        self.title = title.Title()
        self.menu = menu.Menu()
        self.game = game.Game()
        logger.info("App initialized")


    def run(self):
        pyxel.run(self.update, self.draw)

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


pyxel_app = App()


# @sio.on('connect')
# def on_connect(sid, data):
#     pyxel_app.game.handle_connect_event(sid, data)


@sio.on('press')
def on_press(sid, data):
    pyxel_app.game.handle_press_event(sid, data)


@sio.on('release')
def on_release(sid, data):
    pyxel_app.game.handle_release_event(sid, data)


@sio.on('ready')
def on_ready(sid, data):
    pyxel_app.game.handle_connect_event(sid, data)

@sio.on('disconnect')
def on_disconnect(sid):
    pyxel_app.game.handle_disconnect_event(sid)


def say_hello(request):
    return web.Response(text='Hello, world')


server_app = web.Application()
sio.attach(server_app)
server_app.add_routes([web.get('/', say_hello)])
handler = server_app.make_handler()
server = loop.create_server(handler, host='0.0.0.0', port=8080)


def aiohttp_server():
    loop.run_until_complete(server)
    loop.run_forever()


server_thread = threading.Thread(target=aiohttp_server)

server_thread.start()
pyxel_app.run()
