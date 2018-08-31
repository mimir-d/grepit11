from labyrinth import BotAI

class Bot(BotAI):

    speed = 2

    coordinates = []

    vector_x = -40
    vector_y = 40

    index = 0

    def update(self, cast_laser): 

        t, right = cast_laser(1, 0)
        text = 'linia de dreapta'
        print(text, right)

        t, left = cast_laser(-1, 0)
        text = 'linia de stanga'
        print(text, left)
        
        t, down = cast_laser(0, -1)
        text = 'linia de jos'
        print(text, down)
        
        t, top = cast_laser(0, 1)
        text = 'linia de sus'
        print(text, top)

        # create a dictionary and add the coordinates to the array
        c = {
            "top": top,
            "right": right,
            "down": down,
            "left": left,
        }
        self.coordinates.append(c)

        # keep only the last two coordinates
        if len(self.coordinates) >= 3 :
            self.coordinates.pop(0)

        if len(self.coordinates) == 2 :
            if self.coordinates[0] == self.coordinates[1] :
                
                # colision detected

                if self.index % 4 == 0:
                    self.vector_x = 0
                    self.vector_y = -40
                elif self.index % 4 == 1:
                    self.vector_x = 40
                    self.vector_y = 0
                elif self.index % 4 == 2:
                    self.vector_x = 0
                    self.vector_y = 40
                elif self.index % 4 == 3:
                    self.vector_x = -40
                    self.vector_y = 0

                self.index = self.index + 1

        return self.vector_x, self.vector_y


        #if (left >= 1.005 or top >= 1.005) and (self.left_corner_touched == 0):
        #    return -2, 2
        #else:
        #    self.left_corner_touched = 1
        #    return 0, -2
        #if d 

        # regula mainii de dreapta
        # se duce in capat stanga sus
        # mereu verifica daca poate merge pe dreapta
        # daca nu poate - inainte
        # daca poate - dreapta
        #return -1,0
        #