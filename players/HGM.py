
from labyrinth import BotAI

GreenFound = 0
WallFound = 0
SmallestValue_Global = 0
SmallestValueID_Global = 0
Dist_Global = 3
MoveAxis_Global_x = 0
MoveAxis_Global_y = 0
ReadyToRide_Global = 0
InitialChoise_Global = 0
Cicle_Global = 0
laststep1 = 0
laststep2 = 0
laststep3 = 0

class Bot(BotAI):
    def update(self, cast_laser):
        MoveAxis_Global_x = 0
        MoveAxis_Global_y = 0
        if GreenFound == 0:
            name1, d1 = cast_laser(1, 0)
            name2, d2 = cast_laser(-1, 0)
            name3, d3 = cast_laser(0, -1)
            name4, d4 = cast_laser(0, 1)
            if name1 == "endgame" or name2 == "endgame" or name3 == "endgame" or name4 == "endgame":
                global GreenFound
                GreenFound = 1
            raycasts = [d1, d2, d3, d4]
            if WallFound == 0:
                #stabilim cel mai apropiat perete
                SmallestValue = raycasts[0]
                SmallestValueID = 0
                for x in range(0, 3):
                    if SmallestValue>raycasts[x]:
                        SmallestValue = raycasts[x]
                        SmallestValueID = x
                global SmallestValue_Global
                global SmallestValueID_Global
                global WallFound
                SmallestValue_Global = SmallestValue
                SmallestValueID_Global = SmallestValueID
                WallFound = 1
                Dist_Global = SmallestValue_Global
            if WallFound == 1 and Dist_Global > 1.5:
                #mergem la cel mai apropiat perete
                global Dist_Global
                global MoveAxis_Global_x
                global MoveAxis_Global_y
                if SmallestValueID_Global == 0:
                    MoveAxis_Global_x = 5
                    MoveAxis_Global_y = 0
                    useless, Dist_Global = cast_laser(1, 0)
                if SmallestValueID_Global == 1:
                    MoveAxis_Global_x = -5
                    MoveAxis_Global_y = 0
                    useless, Dist_Global = cast_laser(-1, 0)
                if SmallestValueID_Global == 2:
                    MoveAxis_Global_x = 0
                    MoveAxis_Global_y = -5
                    useless, Dist_Global = cast_laser(0, -1)
                if SmallestValueID_Global == 3:
                    MoveAxis_Global_x = 0
                    MoveAxis_Global_y = 5
                    useless, Dist_Global = cast_laser(0, 1)
            if Dist_Global < 1.5:
                global ReadyToRide_Global
                ReadyToRide_Global = 1
            if ReadyToRide_Global == 1 :
                #incepem sa mergem pe cel mai apropiat perete
                global MoveAxis_Global_x
                global MoveAxis_Global_y
                global InitialChoise_Global
                global SmallestValueID_Global
                global Cicle_Global
                if Cicle_Global == 0:
                    
                    if SmallestValueID_Global == 0:
                        MoveAxis_Global_x = 0
                        MoveAxis_Global_y = 5
                    if SmallestValueID_Global == 1:
                        MoveAxis_Global_x = 0
                        MoveAxis_Global_y = -5
                    if SmallestValueID_Global == 2:
                        MoveAxis_Global_x = 5
                        MoveAxis_Global_y = 0
                    if SmallestValueID_Global == 3:
                        MoveAxis_Global_x = -5
                        MoveAxis_Global_y = 0
                    useless, d1 = cast_laser(1, 0)
                    useless, d2 = cast_laser(-1, 0)
                    useless, d3 = cast_laser(0, -1)
                    useless, d4 = cast_laser(0, 1)
                    raycasts = [d1, d2, d3, d4]
                    for x in range(0, 4):
                        if raycasts[x]<1.5 and SmallestValueID_Global!=x:
                            Cicle_Global = 1
                    

                if Cicle_Global == 1:
                    global laststep1
                    global laststep2
                    global laststep3
                    laststep3 = laststep2
                    laststep2 = laststep1
                    laststep1 = SmallestValueID_Global
                    useless, d1 = cast_laser(1, 0)
                    useless, d2 = cast_laser(-1, 0)
                    useless, d3 = cast_laser(0, -1)
                    useless, d4 = cast_laser(0, 1)
                    if d1 < 1.5 and SmallestValueID_Global != 0:
                        SmallestValueID_Global = 0
                    else:
                        if d2 < 1.5 and SmallestValueID_Global != 1:
                            SmallestValueID_Global = 0
                            print (laststep1)
                            print (laststep2)
                            print (laststep3)
                        else:
                            if d3 < 1.5 and SmallestValueID_Global != 2:
                                SmallestValueID_Global = 2
                                
                            else:
                                if d4 < 1.5 and SmallestValueID_Global != 3: 
                                    SmallestValueID_Global = 3
                                
                    Cicle_Global = 0
                    

                
                    
  
        if GreenFound == 1 :
            global MoveAxis_Global_x 
            name1, d1 = cast_laser(1, 0)
            name2, d2 = cast_laser(-1, 0)
            name3, d3 = cast_laser(0, -1)
            name4, d4 = cast_laser(0, 1)
            if name1 == "endgame" :
                MoveAxis_Global_y = 0
                MoveAxis_Global_x = 5
            if name2 == "endgame" :
                MoveAxis_Global_y = 0
                MoveAxis_Global_x = -5
            if name3 == "endgame" :
                MoveAxis_Global_y = -5
                MoveAxis_Global_x = 0
            if name4 == "endgame" :
                MoveAxis_Global_y = 5
                MoveAxis_Global_x = 0
            
    
        

        return MoveAxis_Global_x, MoveAxis_Global_y
