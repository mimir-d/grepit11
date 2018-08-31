
import random
import math
import os, sys
import time
import importlib
import traceback
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont
from pyglet import (graphics, gl)
from pyglet.image import ImageData

import cocos
from cocos.batch import BatchableNode
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


class EntityPhysicsMixin:
    '''
    Mixin that specifies that the entity is physical
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.physics_body = None

    def init_physics(self, world):
        '''
        Initialize the physics for this entity. Must be implemented
        '''
        raise NotImplementedError('mandatory')


class _EntityNode(BatchableNode):
    '''
    CocosNode used as an aggregate in Entity object.
    Restricts the interface presented to inheritants of Entity
    '''
    def __init__(self, entity):
        super().__init__()
        self.__owner = entity

    def draw(self):
        self.__owner.render()


class Entity:
    '''
    Basically an interface for the entity, must implement render, update optional.
    '''
    def __init__(self, node = None):
        self.__node = node or _EntityNode(self)
        self.__node.owner = self

    def render(self):
        '''
        Called each frame for entity rendering
        '''
        raise NotImplementedError('mandatory')

    def update(self):
        '''
        Called each frame for any entity updates.
        Intended to be overwritten
        '''
        pass

    @property
    def cocos_node(self):
        return self.__node


class PrimitiveEntity(EntityPhysicsMixin, Entity):
    '''
    Game entity that renders as primitives
    '''
    PRIMITIVE_LINES = 0
    PRIMITIVE_POLY = 1

    def __init__(self, primitive_type, color):
        super().__init__()
        self.__primitive_type = primitive_type
        self.__color = color

    def __draw_lines(self):
        vert_buf = []
        color_buf = []

        # get a list of disjoint lines and draw them separately with width 1px
        # doesnt matter which fixture contains the lines, all are drawn
        for fixture in self.physics_body.fixtures:
            verts = [(self.physics_body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend(self.__color)

        graphics.draw(len(vert_buf) // 2, gl.GL_LINES, ('v2f', vert_buf), ('c4B', color_buf))

    def __draw_poly(self):
        for fixture in self.physics_body.fixtures:
            # get a list of vertices from the physical fixture and draw them as a filled poly
            verts = [(self.physics_body.transform * v) * Mechanics.PX_PER_METER for v in fixture.shape.vertices]

            vert_buf = []
            color_buf = []
            for v in verts:
                vert_buf.extend([v.x, v.y])
                color_buf.extend(self.__color)

            graphics.draw(len(vert_buf) // 2, gl.GL_POLYGON, ('v2f', vert_buf), ('c4B', color_buf))

    def render(self):
        if self.__primitive_type == self.PRIMITIVE_LINES:
            return self.__draw_lines()
        elif self.__primitive_type == self.PRIMITIVE_POLY:
            return self.__draw_poly()

        # else return nothing and draw nothing


class SpriteEntity(EntityPhysicsMixin, Entity):
    '''
    Game entity that renders as a circle sprite
    '''
    def __init__(self, size, color):
        self.__node = self.__create_cocos_node(size, color)
        super().__init__(self.__node)

    def update(self):
        self.__node.position = (
            self.physics_body.worldCenter.x * Mechanics.PX_PER_METER,
            self.physics_body.worldCenter.y * Mechanics.PX_PER_METER
        )

    def __create_cocos_node(self, size, color):
        im = Image.new('RGBA', (int(size), int(size)), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse((1, 1, im.size[0]-1, im.size[1]-1), fill=color)

        data = ImageData(*im.size, 'RGBA', im.tobytes(), pitch=-im.size[0]*4)
        return Sprite(data)


class Hitmap(Entity):
    '''
    Game entity that renders as a transparent overlay in order to show the laser hits.
    '''
    def __init__(self, width, height):
        super().__init__()
        self.__image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        self.__draw = ImageDraw.Draw(self.__image)

    def draw_hit(self, x, y):
        '''
        Draw a hitpoint on the specified coords
        '''
        y = self.__image.size[1] - y
        self.__draw.ellipse((x-2, y-2, x+2, y+2), fill=(255, 0, 255, 255))

    def render(self):
        data = ImageData(*self.__image.size, 'RGBA', self.__image.tobytes(), pitch=-self.__image.size[0]*4)
        data.blit(0, 0)


class LabyrinthBounds(PrimitiveEntity):
    '''
    Game entity for the playpen walls
    '''
    def __init__(self):
        super().__init__(PrimitiveEntity.PRIMITIVE_LINES, color=(0, 0, 0, 255))

    def init_physics(self, world):
        [x0, y0, x1, y1] = Mechanics.BOUNDS

        self.physics_body = world.CreateStaticBody(
            position=(0, 0),
            shapes=[
                # bottom, top
                b2.edgeShape(vertices=[(x0, y0), (x1, y0)]),
                b2.edgeShape(vertices=[(x0, y1), (x1, y1)]),

                # left, right
                b2.edgeShape(vertices=[(x0, y0), (x0, y1)]),
                b2.edgeShape(vertices=[(x1, y0), (x1, y1)]),
            ],
            userData=Mechanics.WALL_TAG
        )


class Labyrinth(PrimitiveEntity):
    '''
    Game entity for the actual labyrinth walls
    '''
    def __init__(self):
        super().__init__(PrimitiveEntity.PRIMITIVE_LINES, color=(0, 0, 0, 255))

    def init_physics(self, world):
        [x0, y0, x1, y1] = Mechanics.BOUNDS

        self.physics_body = world.CreateStaticBody(
            position=(0, 0),
            shapes=[
                # simple demo one
                # b2.edgeShape(vertices=[(x1/2, y0 + 4), (x1/2, y1)]),
                # b2.edgeShape(vertices=[(x1/2 + 4, y1/2), (x1, y1/2)])

                b2.edgeShape(vertices=[(x0 + 4, y1/2 + 2), (x1/2, y1)]),

                b2.edgeShape(vertices=[(x0, y1/3), (x1/3, y1/3)]),
                b2.edgeShape(vertices=[(x1/3, y1/3), (x1/3, y1/3 - 4)]),
                b2.edgeShape(vertices=[(x1/3, y1/3), (x1/3, y1/3 + 4)]),

                b2.edgeShape(vertices=[(x1/2, y0), (x1/2, y0 + 6)]),
                b2.edgeShape(vertices=[(x1/2, y0 + 6), (x1 * 0.75, y0 + 4)]),
                b2.edgeShape(vertices=[(x1 * 0.75, y0 + 4), (x1 * 0.75, y1/2)]),

                b2.edgeShape(vertices=[(x1/2, y1 * 0.75 + 1.5), (x1/2, y1)]),

                b2.edgeShape(vertices=[(x1/2, y1 * 0.75), (x1/2 + 2, y1 * 0.75)]),
                b2.edgeShape(vertices=[(x1/2 + 2, y1 * 0.75), (x1/2 + 2, y1/3)]),
                b2.edgeShape(vertices=[(x1/2, y1/3), (x1/2 + 2, y1/3)]),
                b2.edgeShape(vertices=[(x1/2, y1 * 0.75), (x1/2, y1/3)]),

                b2.edgeShape(vertices=[(x1/2 + 2, y1 * 0.75), (x1 - 6, y1 * 0.65)]),

                b2.edgeShape(vertices=[(x1, y1), (x1 - 3.5, y1 * 0.65)]),

                b2.edgeShape(vertices=[(x1, y1/2), (x1 - 3.5, y0 + 4)])
            ],
            userData=Mechanics.WALL_TAG
        )


class Bot(SpriteEntity):
    '''
    Game entity for the bot that the AI has to control
    '''
    __SIZE = 1

    def __init__(self, position):
        super().__init__(self.__SIZE * Mechanics.PX_PER_METER * 2, color=(255, 0, 0, 255))
        self.__initial_pos = position

    def init_physics(self, world):
        self.physics_body = world.CreateDynamicBody(
            position=self.__initial_pos,
            userData=Mechanics.ENDGAME_TAG
        )
        self.physics_body.CreateCircleFixture(radius=self.__SIZE, density=1, friction=0.3)


class LandingZone(PrimitiveEntity):
    '''
    Game entity for the target object where the bot needs to arrive
    '''
    def __init__(self, position):
        super().__init__(PrimitiveEntity.PRIMITIVE_POLY, color=(0, 255, 0, 100))
        self.__initial_pos = position

    def init_physics(self, world):
        self.physics_body = world.CreateStaticBody(
            position=self.__initial_pos,
            shapes=b2.polygonShape(box=(2, 2)),
            userData=Mechanics.ENDGAME_TAG
        )


class RaycastInterceptor(b2.rayCastCallback):
    '''
    Raycast callback used in the laser targetting. Returns the userData of the intersected
    fixture body, which results in walls or targets
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__type = None
        self.__point = None

    def ReportFixture(self, fixture, point, normal, fraction):
        self.__type = fixture.body.userData
        self.__point = point
        # stop at closest point, docs say to return fraction
        return fraction

    @property
    def type(self):
        return self.__type

    @property
    def point(self):
        return self.__point


class Mechanics:
    '''
    Game mechanics object
    Deals with physics, the laser raycasts and endgame condition
    '''
    PHYS_WIDTH = 30.0
    PHYS_HEIGHT = 30.0
    PX_PER_METER = 20.0

    ENDGAME_TAG = 'endgame'
    WALL_TAG = 'wall'

    BOUNDS = (0.5, 0.5, PHYS_WIDTH - 0.5, PHYS_HEIGHT - 0.5)

    BOT_POSITION = (8, 25)
    LANDING_POSITION = (BOUNDS[2]/2 + 6, BOUNDS[3] - 2)

    def __init__(self):
        self.__world = b2.world(gravity=(0, 0), doSleep=True)
        self.__entities = []

        self.hitmap = None
        self.target_reached = EventOnce()

    def add_entity(self, entity):
        entity.init_physics(self.__world)
        self.__entities.append(entity)

    def update(self, dt):
        self.__world.Step(1.0 / 60, 10, 10)

        # update all entities
        for e in self.__entities:
            e.update()

        # check contacts for endgame
        for c in self.__world.contacts:
            d1 = c.fixtureA.body.userData
            d2 = c.fixtureB.body.userData
            # both the bot and the target have this userData tag, so if they're equal
            # this means they've collided and game is done
            if d1 == d2 and d1 == Mechanics.ENDGAME_TAG:
                self.target_reached()
                break

    def raycast(self, src, dst):
        '''
        Does a raycast from src to dst points in 2d space.
        Returns: (object_type, distance_to_object)
        '''
        ri = RaycastInterceptor()
        self.__world.RayCast(ri, src, dst)

        # draw on hitmap
        if self.hitmap is not None:
            x = ri.point[0] * Mechanics.PX_PER_METER
            y = ri.point[1] * Mechanics.PX_PER_METER
            self.hitmap.draw_hit(x, y)

        # TODO:
        # vert_buf = [float(x) for x in [src[0], src[1], ri.point[0], ri.point[1]]]
        # color_buf = [255, 0, 0, 0, 0, 255]
        # graphics.draw(len(vert_buf) // 2, gl.GL_LINES, ('v2f', vert_buf), ('c3B', color_buf))
        dx = ri.point[0] - src[0]
        dy = ri.point[1] - src[1]
        mag = (dx*dx + dy*dy) ** 0.5

        return ri.type, mag


class Main(ColorLayer):
    '''
    Main cocos2d drawing surface and scene
    '''
    WIDTH = int(Mechanics.PHYS_WIDTH * Mechanics.PX_PER_METER)
    HEIGHT = int(Mechanics.PHYS_HEIGHT * Mechanics.PX_PER_METER)

    def __init__(self):
        super(Main, self).__init__(52, 152, 219, 255)

        # init the mechanics
        self.__mechanics = Mechanics()
        self.__mechanics.target_reached += self.__on_target_reached
        self.__mechanics.hitmap = self.__add_hitmap()

        # add all the objects
        self.__add_labyrinth()
        self.__add_landing()
        self.__add_bot()

        # start timer and begin
        self.__start_time = time.time()
        self.schedule(self.__mechanics.update)

    def __on_target_reached(self):
        # inactivate the bot and wait for exit
        bot_node = self.__bot.cocos_node
        bot_node.remove_action(bot_node.actions[0])

        total = time.time() - self.__start_time
        print('total time was {} seconds'.format(total))

    def __add_bot(self):
        try:
            mod = importlib.import_module('players.{}'.format(sys.argv[1]))
        except:
            raise RuntimeError('Cannot load AI module. Inner error: ', traceback.format_exc())

        self.__bot = Bot(Mechanics.BOT_POSITION)
        action = MoveAction(mod.Bot(), self.__mechanics)
        self.__bot.cocos_node.do(action)
        self.add(self.__bot)

    def __add_hitmap(self):
        hitmap = Hitmap(self.WIDTH, self.HEIGHT)
        super().add(hitmap.cocos_node, z=1)
        return hitmap

    def __add_labyrinth(self):
        self.add(LabyrinthBounds())
        self.add(Labyrinth())

    def __add_landing(self):
        self.add(LandingZone(Mechanics.LANDING_POSITION))

    def add(self, obj, *args, **kwargs):
        ''' Override add() that adds physical objects as well '''
        super(Main, self).add(obj.cocos_node, *args, **kwargs)
        self.__mechanics.add_entity(obj)


class MoveAction(act.Move):
    '''
    The cocos2d node move action that interfaces with the AI
    '''
    def __init__(self, ai, mechanics):
        super().__init__()
        self.__ai = ai
        self.__mechanics = mechanics

    def step(self, dt):
        try:
            dx, dy = self.__ai.update(self.__raycast)
        except Exception as e:
            # any exception in user script results in a null movement vector
            print('{} threw exception: {}'.format(self.target, traceback.format_exc()))
            dx, dy = 0, 0

        # act on the body with the input, linear motion
        body = self.target.owner.physics_body
        dx -= body.linearVelocity[0]
        dy -= body.linearVelocity[1]
        body.ApplyLinearImpulse(b2Vec2(dx, dy) * body.mass, body.worldCenter, wake=True)

    def __raycast(self, dx, dy):
        entity = self.target.owner
        px = entity.physics_body.position.x
        py = entity.physics_body.position.y

        # make a distant point
        magi = 1.0 / ((dx*dx + dy*dy) ** 0.5)
        x = px + dx * magi * 99
        y = py + dy * magi * 99
        return self.__mechanics.raycast(src=(px, py), dst=(x, y))

    def __deepcopy__(self, memo):
        # the cocos framework does a deepcopy on the action and we need refs, so skip that
        return self


class BotAI:
    def update(self, cast_laser):
        '''
        Returns a movement vector
        '''
        raise NotImplementedError('overwrite this')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid num of args; syntax is: python {} <ai module name>'.format(sys.argv[0]))
        exit(1)

    director.init(width=Main.WIDTH, height=Main.HEIGHT, autoscale=True, resizable=True)
    director.run(cocos.scene.Scene(Main()))
