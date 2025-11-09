# ============================================================
# student.py – Spielfigur
# Kann: bewegen, graben, antworten, sammeln, PowerUps nutzen.
# ============================================================

from .entity import Entity, GridPos, Direction
from .level import GRID_W, GRID_H
from .block import Block
from .enemy import Enemy
from .collectibles import Collectible
from .powerups import PowerUp

class Student(Entity):
    def __init__(self, pos: GridPos):
        super().__init__(pos, speed=10.0)
        self.diggingSpeed = 1.0
        self.answersBuffer = 0
        self.invulnerableUntil = 0.0
        self.hasPizzaShield = False
        self.stunnedUntil = 0.0
        # Callbacks (damit Collectibles ECTS gutschreiben können)
        self.on_gain_ects = None  # wird im Game gesetzt

    def move(self, dir_):
        nx = max(0, min(GRID_W - 1, self.position.x + dir_[0]))
        ny = max(0, min(GRID_H - 1, self.position.y + dir_[1]))
        self.position = GridPos(nx, ny)

    def dig(self, level) -> None:
        b: Block = level.blocks[self.position.x][self.position.y]
        if not b.isDestroyed:
            b.destroy()

    def answer(self, target: Enemy) -> None:
        # simple Kampflogik – später erweitern (ChatGPT-Boost etc.)
        target.takeAnswer()
        if self.answersBuffer > 0:
            self.answersBuffer -= 1

    def collect(self, item: Collectible) -> None:
        item.onPickUp(self)

    def use(self, power: PowerUp) -> None:
        power.applyTo(self)
