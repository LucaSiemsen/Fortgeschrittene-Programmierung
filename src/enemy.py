# ============================================================
# enemy.py – Gegnerbasis + Dozent/Klausur
# Dozent: 1 HP, Klausur: 5 HP (ChatGPT kann später auf 1 setzen).
# ============================================================

from .entity import Entity, GridPos

class Enemy(Entity):
    def __init__(self, pos: GridPos, hp: int = 1, damage: int = 1):
        super().__init__(pos, speed=0.0)
        self.hp = hp
        self.damage = damage

    def onTouched(self, student) -> None:
        # TODO: Kontaktfolgen (z. B. Stun/Schaden/Timer)
        pass

    def takeAnswer(self) -> None:
        self.hp -= 1

class Dozent(Enemy):
    def __init__(self, pos: GridPos):
        super().__init__(pos, hp=1)

class Klausur(Enemy):
    def __init__(self, pos: GridPos):
        super().__init__(pos, hp=5)
