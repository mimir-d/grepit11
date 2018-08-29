
import random
import math
import os
import importlib
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont
from pyglet import (graphics, gl)
from pyglet.image import ImageData

import cocos
from cocos.cocosnode import CocosNode
import cocos.actions as act
import cocos.euclid as eu
from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.text import Label
from cocos.director import director

from Box2D import (b2, b2Vec2)


class Event:
    '''
    Event object that can call multiple observer functions with arbitrary args
    '''
    def __init__(self):
        self.__observers = []

    def __iadd__(self, cb):
        self.__observers.append(cb)
        return self

    def __isub__(self, cb):
        self.__observers.remove(cb)
        return self

    def __call__(self, *args, **kwargs):
        for o in self.__observers:
            o(*args, **kwargs)


class BotSpriteEntity(Sprite):
    '''
    The player controlled bot
    '''
    def __init__(self, size, color):
        super(BotEntity, self).__init__(self.__create_image(size, color))

    def __create_image(self, size, color):
        im = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        return ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)


class Mechanics:
    '''
    Game mechanics object
    Deals with physics
    '''
    PX_PER_METER = 20.0

    def __init__(self):
        # todo: contact listener for end game
        self.__world = b2.world(gravity=(0, -10), doSleep=True)

        self.__entities = []
        self.target_reached = Event()

    def add_entity(self, entity):
        # init mechanics for given entity
        self.__init_entity(entity)


        # append to known entities
        self.__entities.append(entity)

    def update(self, dt):
        self.__world.Step(1.0 / 60, 10, 10)

    def __init_entity(self, entity):
        entity.init_phys(self.__world)


class Entity(CocosNode):
    def __init__(self):
        super().__init__()
        self._body = None

    def draw(self):
        for fixture in self._body.fixtures:
            verts = [(self._body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]
            # import pdb; pdb.set_trace()

            vert_buf = []
            color_buf = []
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend([255, 0, 0])

            graphics.draw(len(vert_buf) // 2, gl.GL_POLYGON, ('v2f', vert_buf), ('c3B', color_buf))


class LabyrinthBounds(Entity):
    def init_phys(self, world):
        x0 = 10 / Mechanics.PX_PER_METER
        y0 = 10 / Mechanics.PX_PER_METER
        x1 = (Main.WIDTH - 10) / Mechanics.PX_PER_METER
        y1 = (Main.HEIGHT - 10) / Mechanics.PX_PER_METER

        self._body = world.CreateStaticBody(
            position=(0, 0),
            shapes=[
                # bottom, top
                b2.edgeShape(vertices=[(x0, y0), (x1, y0)]),
                b2.edgeShape(vertices=[(x0, y1), (x1, y1)]),

                # left, right
                b2.edgeShape(vertices=[(x0, y0), (x0, y1)]),
                b2.edgeShape(vertices=[(x1, y0), (x1, y1)]),
            ]
        )

    def draw(self):
        vert_buf = []
        color_buf = []

        for fixture in self._body.fixtures:
            verts = [(self._body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend([0, 0, 0])

        print(vert_buf)
        graphics.draw(len(vert_buf) // 2, gl.GL_LINES, ('v2f', vert_buf), ('c3B', color_buf))


class Ball(Entity):
    def init_phys(self, world):
        self._body = world.CreateDynamicBody(
            position=(10, 15), angle=15
        )
        self._body.CreatePolygonFixture(box=(1, 1), density=1, friction=0.3)

# full of goddamn hacks because i have to write this with no sleep
keys = set()

class Main(ColorLayer):
    WIDTH = 600
    HEIGHT = 600

    is_event_handler = True

    def on_key_press(self, key, mods):
        global keys
        keys.add(key)

    def on_key_release(self, key, mods):
        global keys
        keys.remove(key)

    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 255)

        self.__mechanics = Mechanics()
        self.__mechanics.target_reached += self.__on_target_reached

        # self.__init_players()
        self.add(LabyrinthBounds())
        ball = Ball()
        self.add(ball)

        ball.do(MoveAI())

        self.schedule(self.__mechanics.update)

    def __on_target_reached(self):
        print('total time was')

    def add(self, obj, *args, **kwargs):
        ''' Override add() that adds physical objects as well '''
        super(Main, self).add(obj, *args, **kwargs)
        self.__mechanics.add_entity(obj)

class MoveAI(act.Move):
    def step(self, dt):
        global keys
        dx = 0
        dy = 0
        if 65361 in keys:
            # left
            dx = -1
        if 65363 in keys:
            # right
            dx = 1
        if 65362 in keys:
            # up
            dy = 1
        if 65364 in keys:
            # down
            dy = -1
        b = self.target._body
        b.ApplyLinearImpulse(b2Vec2(dx, dy) * b.mass, b.worldCenter, wake=True)


if __name__ == '__main__':
    director.init(width=Main.WIDTH, height=Main.HEIGHT, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
