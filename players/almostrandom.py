from labyrinth import BotAI
import random
from math import sin, cos, radians, fabs, degrees

class Bot(BotAI):
    first = True
    last = 0
    old_x = 0
    old_y = 0
    x = 0
    y = 0
    inMove = False
    alph = 0
    offset = 0
    up = None
    down = None
    left = None
    right = None
    frame = 0
    interv = 0
    already = False;
    passed = False;

    def update(self, cast_laser):
        t, up = cast_laser(1, 0)
        t, down = cast_laser(0, 1)
        t, left = cast_laser(-1, 0)
        t, right = cast_laser(0, -1)

        if up == self.up and down == self.down and right == self.right and left == self.left:
            self.frame += 1
        else:
            self.frame = 0
            self.up = up
            self.down = down
            self.right = right
            self.left = left

        if self.frame > 20:
            # print ("blocked")
            speed = 100
            return random.uniform(-1, 1)*speed, random.uniform(-1, 1)*speed
        if self.inMove == False:
            for i in range(0,360):

                if i>=(self.interv-18 + 360)%360 and i<=(self.interv+18)%360:
                    continue
                alpha = radians(i)
                t, d = cast_laser(cos(alpha), sin(alpha))
                if t=="endgame":
                    self.alph = alpha;
                    self.x = (cos(alpha) * d)/0.016667
                    self.y = (sin(alpha) * d)/0.016667
                    self.inMove = True
                    break
                diff = fabs(self.last - d)
                #print (str(i) + ": " + str(diff))
                self.last = d

                if i != 0 and diff > 2:
                    # print ((cos(alpha) * d, sin(alpha) * d))
                    self.alph = alpha;
                    #offset
                    self.offset = i;
                    self.old_x = self.x
                    self.old_y = self.y
                    self.x = (cos(alpha) * d)/0.016667
                    self.y = (sin(alpha) * d)/0.016667
                    self.inMove = True
                    break

        t,d = cast_laser(cos(self.alph), sin(self.alph))
        self.x = cos(self.alph) * d/0.016667
        self.y = sin(self.alph) * d/0.016667

        if d < 2 and self.inMove:
            self.x = 0;
            self.y = 0;
            self.inMove = False
            self.interv = (180 + int(degrees(self.alph)))%360
            # print (self.interv)
        return self.x, self.y
