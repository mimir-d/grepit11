
from labyrinth import BotAI

class Bot(BotAI):
    def update(self, cast_laser):
        t, d = cast_laser(1, 0)
        print(t, d)
        t, d = cast_laser(-1, 0)
        print(t, d)
        t, d = cast_laser(0, -1)
        print(t, d)
        t, d = cast_laser(0, 1)
        print(t, d)

        return 0, 0
