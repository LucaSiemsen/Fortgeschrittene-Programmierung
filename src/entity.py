# ============================================================
# entity.py – Basiskram: Position, Richtungen, Entity
# Notiz: so schlank halten, damit Student/Enemy es leicht erben können.
# ============================================================

from dataclasses import dataclass

TILE = 32  # Kachelgröße – muss überall konsistent sein

@dataclass
class GridPos:
    x: int
    y: int

class Direction:
    # simple aber praktisch für Grid-Bewegungen
    UP    = (0, -1)
    DOWN  = (0,  1)
    LEFT  = (-1, 0)
    RIGHT = (1,  0)

class Entity:
    """Basisklasse für bewegliche Dinge (Student, Enemy)."""
    def __init__(self, pos: GridPos, speed: float = 6.0):
        self.position = pos
        self.speed = speed  # aktuell ungenutzt (Grid), später evtl. für Animationen

    def update(self, dt: float) -> None:
        """Hook für abgeleitete Klassen – pro Frame aufgerufen."""
        pass
