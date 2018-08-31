
from labyrinth import BotAI
import os
import math
from random import randint
def go_down():
     return 0,-100
def go_right():
     return 0,100
def centralizare(d1, d2, d3, d4):
     if (d4+d3)/2>(d1+d2)/2:
        if d1>d2:
             return d1-d2,0
        elif d2>d1:
             return 0,d2-d1
     elif (d1+d2)/2>(d4+d3)/2:
        if d4>d3:
             return d4-d3,0
        elif d3>d4:
             return 0,d3-d4

def deg2vec(deg):
        return math.cos(math.radians(deg)), math.sin(math.radians(deg))


angle = 45

class Bot(BotAI):
           def update(self, cast_laser):
                global angle
                t1, d1 = cast_laser(1, 0)
                t2, d2 = cast_laser(-1, 0)
                t3, d3 = cast_laser(0, -1)
                t4, d4 = cast_laser(0, 1)
                x, y = deg2vec(angle)
                t, d = cast_laser(x, y)
                if d < 2 :
                        angle = randint(0, 359)
                        x, y = deg2vec(angle)
                return x*500, y*500
##                return centralizare(d1, d2, d3, d4)
##                return go_down()
##                return 100,0
      
            




















##
##
##from labyrinth import BotAI
##import os
##import math
##from random import randint
##def go_down():
##     return 0,-100
##def go_right():
##     return 0,100
##def centralizare(d1, d2, d3, d4):
##     if (d4+d3)/2>(d1+d2)/2:
##        if d1>d2:
##             return d1-d2,0
##        elif d2>d1:
##             return 0,d2-d1
##     elif (d1+d2)/2>(d4+d3)/2:
##        if d4>d3:
##             return d4-d3,0
##        elif d3>d4:
##             return 0,d3-d4
##
##def deg2vec(deg):
##        return math.cos(math.radians(deg)), math.sin(math.radians(deg))
##
##
##angle = 45
##
##class Bot(BotAI):
##           def update(self, cast_laser):
##                global angle
##                t1, d1 = cast_laser(1, 0)
##                t2, d2 = cast_laser(-1, 0)
##                t3, d3 = cast_laser(0, -1)
##                t4, d4 = cast_laser(0, 1)
##                
##                x, y = deg2vec(angle)
##                t, d = cast_laser(x, y)
##                if d < 2 :
##                        angle = randint(0, 359)
##                        x, y = deg2vec(angle)
##                return x*500, y*500
####                return centralizare(d1, d2, d3, d4)
####                return go_down()
####                return 100,0
##
##
##









