from random import *
from labyrinth import BotAI
speed=1000
x=-speed
y=-speed
class Bot(BotAI):
    def update(self, cast_laser):
        global x
        global y
        global speed
        # Distance
        t,left=cast_laser(-1, 0)
        t,right=cast_laser(1, 0)
        t,down=cast_laser(0, -1)
        t,top=cast_laser(0, 1)
        if(left<2):
            x=speed
        if(right<2):
            x=-speed
        if(down<2):
            y=speed
        if(top<2):
            y=-speed
        return x-randint(100,250),y-randint(100,250)
