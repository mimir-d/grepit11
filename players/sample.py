
from labyrinth import BotAI

class Bot(BotAI):
    def update(self, cast_laser):
        t, p = cast_laser(1, 0)
        t, p = cast_laser(-1, 0)
        t, p = cast_laser(0, -1)
        t, p = cast_laser(0, 1)

        return 0, 0
