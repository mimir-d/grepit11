from labyrinth import BotAI
import math

def close(a, b):
    if math.fabs(a-b) < 0.2:
        if a>b:
            return 1, 1
        return 1, 0
    return 0, 0


class Bot(BotAI):

    def __init__(self):
        self.fc = 0
        self.updateble = 1
        self.time1 = 0
        self.x = 0
        self.y = 0
        self.prevunghi = 3.14159



    def update(self, cast_laser):
        #t, d = cast_laser(1, 0)
        #print(t, d)
        #t, d = cast_laser(-1, 0)
        #print(t, d)
        #t, d = cast_laser(0, -1)
        #print(t, d)
        #t, d = cast_laser(0, 1)
        #print(t, d)

        self.fc += 1

        u1 = 0

        while u1 < 3.14159*2:
            t, d = cast_laser(math.sin(u1), math.cos(u1))
            if t == "endgame":
                  a = 0
                  b = 0
                  self.updateble = 0
                  self.time1 = self.fc
                  self.y = math.sin(u1)*15
                  self.y = math.cos(u1)*15
                  self.prevunghi = u1
                  print(d)
                  return math.sin(u1)*105, math.cos(u1)*105
            u1 += 0.1



        if self.updateble == 0:
            if self.fc - self.time1 > 30:
                self.updateble = 1
       
        if self.updateble  == 1:

            unghi = self.prevunghi - 2.14159
            finalu = unghi + 3.14159 * 2
            prevd = -1
            while unghi < finalu:
                t, d = cast_laser(math.sin(unghi), math.cos(unghi))
                
                if prevd == -1:
                    prevd = d

                a, b = close(prevd, d)

                if t == "endgame":
                   a = 0
                   b = 0
    
                if a == 0:
                    if b == 0:
                        unghi +=0.1
                    else:
                        unghi -=0.1

                    self.updateble = 0
                    self.time1 = self.fc
                    self.y = math.sin(unghi)*15
                    self.y = math.cos(unghi)*15
                    self.prevunghi = unghi
                    print(d)
                    return math.sin(unghi)*105, math.cos(unghi)*105

                prevd = d
                unghi += 0.0005
        else:
              return self.x, self.y

        return 0, 0
