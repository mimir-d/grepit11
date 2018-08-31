
from labyrinth import BotAI
import math
import random
import time

#constant declaration
left_dir = (-1, 0)
right_dir = (1, 0)
up_dir = (0, 1)
down_dir = (1, 0)

go4finish = 0
finish = (0,0)
start_time = 0
last_check = 0

def angleToPoint(angle):

    point_x, point_y = 0, 0
    rad = math.radians(angle)

    point_x = math.cos(rad)
    point_y = math.sin(rad) 

    return (point_x, point_y)

def generate_rand_point():
    return angleToPoint(360 * random.random())

def scan_for_destination(cast_laser):

    #print("scan for destination")

    angle_increment = 10
    angle = 0

    while(angle < 360):
        point = angleToPoint(angle)
        t, d = cast_laser(point[0], point[1])

        if(t != "wall"):
            print(t)
            return (1, point)

        angle += angle_increment
    
    return (0, 0)



rand_point = generate_rand_point()

class Bot(BotAI):


    def update(self, cast_laser):

        speed = 10000
        min_dist = 1.5
        global rand_point
        global go4finish
        global finish
        global start_time
        global last_check

        t, d = cast_laser(rand_point[0], rand_point[1])

        #print(t)
        if(go4finish == 1):
            print(time.time() - start_time)

        #bug
        if(go4finish == 1 and time.time() - start_time >= 2):
            go4finish = 0
            while(d < min_dist):
                rand_point = generate_rand_point()
                t, d = cast_laser(rand_point[0], rand_point[1])

        #if we are near our random point pick another one
        if(d < min_dist and go4finish == 0):
            res = scan_for_destination(cast_laser)

            #we can see the finish
            if(res[0] == 1):
                go4finish = 1
                rand_point = res[1]
                print("go for finish!!!")
                start_time = time.time()
                print(rand_point)

            #choose a random point
            else:
                while(d < min_dist):
                    rand_point = generate_rand_point()
                    t, d = cast_laser(rand_point[0], rand_point[1])

                print("random point generated")
                print(rand_point)

        if(time.time() - last_check > 0.1):
            res = scan_for_destination(cast_laser)
            if(res[0] == 1):
                go4finish = 1
                rand_point = res[1]
                print("go for finish!!!")
                start_time = time.time()
                print(rand_point)



        return (rand_point[0] * speed, rand_point[1] * speed)
        
        

