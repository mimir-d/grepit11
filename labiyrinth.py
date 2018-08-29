
import random
import math
import os
import time
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


class EventOnce:
    '''
    Event object that can call multiple observer functions with arbitrary args
    EventOnce acts as a trigger, only broadcasts the data once
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
        del self.__observers[:]


class EntityPhysMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._body = None


class Entity(EntityPhysMixin, CocosNode):
    '''
    Game entity that renders as primitives
    '''
    def draw_lines(self, color):
        vert_buf = []
        color_buf = []

        for fixture in self._body.fixtures:
            verts = [(self._body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend(color)

        graphics.draw(len(vert_buf) // 2, gl.GL_LINES, ('v2f', vert_buf), ('c4B', color_buf))

    def draw_poly(self, color):
        for fixture in self._body.fixtures:
            verts = [(self._body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]

            vert_buf = []
            color_buf = []
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend(color)

            graphics.draw(len(vert_buf) // 2, gl.GL_POLYGON, ('v2f', vert_buf), ('c4B', color_buf))


class SpriteEntity(EntityPhysMixin, Sprite):
    '''
    Game entity that renders as a sprite circle
    '''
    def __init__(self, size, color):
        super().__init__(self.__create_image(size, color))
        self.__size = size

    def __create_image(self, size, color):
        im = Image.new('RGBA', (int(size), int(size)), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        return ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)

    def draw(self):
        x = self._body.worldCenter.x * Mechanics.PX_PER_METER
        y = self._body.worldCenter.y * Mechanics.PX_PER_METER
        self.position = (x, y)

        super().draw()


class LabyrinthBounds(Entity):
    def init_phys(self, world):
        [x0, y0, x1, y1] = Mechanics.getBounds()

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
        self.draw_lines([0, 0, 0, 255])


class Labyrinth(Entity):
    def init_phys(self, world):
        [x0, y0, x1, y1] = Mechanics.getBounds()

        # simple demo one
        self._body = world.CreateStaticBody(
            position=(0, 0),
            shapes=[
                b2.edgeShape(vertices=[(x1/2, y0 + 4), (x1/2, y1)]),
                b2.edgeShape(vertices=[(x1/2 + 4, y1/2), (x1, y1/2)])
            ]
        )

    def draw(self):
        self.draw_lines([0, 0, 0, 255])


class Bot(SpriteEntity):
    __SIZE = 1

    def __init__(self):
        super().__init__(self.__SIZE * Mechanics.PX_PER_METER * 2, (255, 0, 0, 255))

    def init_phys(self, world):
        self._body = world.CreateDynamicBody(
            position=(10, 15),
            userData=Mechanics.ENDGAME_TAG
        )
        self._body.CreateCircleFixture(radius=self.__SIZE, density=1, friction=0.3)


class LandingZone(Entity):
    '''
    The target object where the bot needs to arrive
    '''
    def init_phys(self, world):
        [x0, y0, x1, y1] = Mechanics.getBounds()

        self._body = world.CreateStaticBody(
            position=(x1 - 2, y1 - 2),
            shapes=b2.polygonShape(box=(2, 2)),
            userData=Mechanics.ENDGAME_TAG
        )

    def draw(self):
        self.draw_poly([0, 255, 0, 100])


class Mechanics:
    '''
    Game mechanics object
    Deals with physics
    '''
    PX_PER_METER = 20.0
    ENDGAME_TAG = 'endgame'

    def __init__(self):
        # todo: contact listener for end game
        self.__world = b2.world(gravity=(0, 0), doSleep=True)

        self.target_reached = EventOnce()

    def add_entity(self, entity):
        # init mechanics for given entity
        self.__init_entity(entity)

    def update(self, dt):
        self.__world.Step(1.0 / 60, 10, 10)

        # check contacts for endgame
        for c in self.__world.contacts:
            d1 = c.fixtureA.body.userData
            d2 = c.fixtureB.body.userData
            if d1 == d2:
                self.target_reached()
                break

    def __init_entity(self, entity):
        entity.init_phys(self.__world)

    @staticmethod
    def getBounds():
        x0 = 10 / Mechanics.PX_PER_METER
        y0 = 10 / Mechanics.PX_PER_METER
        x1 = (Main.WIDTH - 10) / Mechanics.PX_PER_METER
        y1 = (Main.HEIGHT - 10) / Mechanics.PX_PER_METER
        return [x0, y0, x1, y1]


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

        self.add(LabyrinthBounds())
        self.add(Labyrinth())

        self.__bot = Bot()
        self.add(self.__bot)

        self.__bot.do(MoveAI())

        self.add(LandingZone())

        self.__start_time = time.time()
        self.schedule(self.__mechanics.update)

    def __on_target_reached(self):
        self.__bot.remove_action(self.__bot.actions[0])

        total = time.time() - self.__start_time
        print('total time was {} seconds'.format(total))


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
