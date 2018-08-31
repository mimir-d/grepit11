# CLAUDIU NEAMTU
from labyrinth import BotAI

direction = 0
go_to_start = True
right_rotation = 0
x = y = 0
speed = 100
max_slow = 80

def dreapta(x, y):
    x = x + speed
    return x, y

def stanga(x, y):
    x = x - speed
    return x, y

def sus(x, y):
    y = y + speed
    return x, y

def jos(x, y):
    y = y - speed
    return x, y

go = [dreapta, sus, stanga, jos]


def realist_direction(direction):
    if direction > 3:
        return 0
    if direction < 0:
        return 3
    return direction


class Bot(BotAI):
    def update(self, cast_laser):
        dist = []
        t, d = cast_laser(1, 0)
        dist.append(d)
        t, d = cast_laser(0, 1)
        dist.append(d)
        t, d = cast_laser(-1, 0)
        dist.append(d)
        t, d = cast_laser(0, -1)
        dist.append(d)

        global x
        global y
        global speed
        global direction
        global go_to_start
        global right_rotation
        global max_slow
        x = y = 0

        if go_to_start:
            if dist[1] > 1.5:
                x, y = go[1](x, y)
            #if dist[1] > 1.5:
            #    x, y = go[1](x, y)
            #if dist[0] <= 1.5 and dist[1] <= 1.5:
            else:
                go_to_start = False
                direction = 2
        elif right_rotation == 0:
            dist_fata = dist[direction]
            dist_dreapta = dist[realist_direction(direction - 1)]

            if dist_fata > 1.4 and dist_dreapta < 7:
                if dist_dreapta > 1.4:
                    x, y = go[realist_direction(direction - 1)](x, y)
                    if max_slow > 0:
                        speed = speed - max_slow * 0.2
                        max_slow -= max_slow * 0.2
                else:
                    x, y = go[direction](x, y)
            else:
                if dist_dreapta >= 10:
                    right_rotation = 1
                else:
                    direction = realist_direction(direction + 1)

        if right_rotation >= 1:
            if right_rotation == 1:
                a = speed
                speed = 100
                x, y = go[direction](x, y)
                speed = a
            elif right_rotation == 2:
                direction = realist_direction(direction - 1)
            elif right_rotation == 3:
                a = speed
                speed = 100
                x, y = go[direction](x, y)
                speed = a
            else:
                right_rotation = 0
                return x, y
            right_rotation += 1

        return x, y
