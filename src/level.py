# ============================================================
# level.py – Raster, Gegner/Items, ECTS-Ziel & Timer
# TODO: Level aus Datei laden (ASCII-Map) – später nice to have.
# ============================================================

from typing import List
from .block import Block
from .enemy import Enemy
from .collectibles import Collectible
from .powerups import PowerUp
from .timer import BafoegTimer

GRID_W, GRID_H = 20, 14

class Level:
    def __init__(self, idx: int = 1, required_ects: int = 3, start_time: int = 60):
        self.index = idx
        self.requiredECTS = required_ects
        self.blocks: List[List[Block]] = [[Block(False) for _ in range(GRID_H)] for _ in range(GRID_W)]
        self.enemies: List[Enemy] = []
        self.collectibles: List[Collectible] = []
        self.powerUps: List[PowerUp] = []
        self.timer = BafoegTimer(start_time)
        self.collectedECTS = 0

    def load(self) -> None:
        # Platzhalter – später: Spawns/Map aus Datei
        pass

    def update(self, dt: float) -> None:
        self.timer.tick(dt)

    def isCleared(self) -> bool:
        return self.collectedECTS >= self.requiredECTS
