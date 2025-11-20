# ============================================================
# level.py – Herzstück der Spiellogik
# ------------------------------------------------------------
# Dieses Level-Objekt kümmert sich um:
#   - Grid aus SOLID/EMPTY-Tiles
#   - ECTS (gelbe Kästchen)
#   - PowerUps (Pizza, Party, ChatGPT)
#   - Professoren, die sich bewegen & Fragen stellen
#   - BAföG-Timer und Win/Lose-Status
# ============================================================

from __future__ import annotations

import random
from typing import Optional

import pygame

from .config import (
    GRID_COLS,
    GRID_ROWS,
    GRID_MARGIN_X_TILES,
    GRID_MARGIN_Y_TILES,
    BAFOEG_TIME_SECONDS,
    REQUIRED_ECTS,
    QUESTIONS_BY_PROF,
    PROFESSORS,
)
from .graphics import Sprite
from .enemy import ProfessorEnemy
from .timer import BafoegTimer
from .powerups import PowerUp, PowerUpType


class TileType:
    SOLID = 0   # Erde / Buchblock
    EMPTY = 1   # Tunnel


class Tile:
    """Repräsentiert einen Block im Grid."""

    def __init__(self, ttype: int):
        self.type = ttype

    @property
    def is_solid(self) -> bool:
        return self.type == TileType.SOLID

    @property
    def is_empty(self) -> bool:
        return self.type == TileType.EMPTY

    def dig(self) -> None:
        """Aus Erde wird Tunnel."""
        self.type = TileType.EMPTY


class ECTS:
    """Gelber Sammelpunkt – 1 ECTS pro Stück."""

    def __init__(self, gx: int, gy: int, tile_size: int):
        self.gx = gx
        self.gy = gy
        self.tile_size = tile_size

    def draw(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        px = offset_x + self.gx * self.tile_size
        py = offset_y + self.gy * self.tile_size
        s = self.tile_size // 5
        rect = pygame.Rect(
            px + s,
            py + s,
            self.tile_size - 2 * s,
            self.tile_size - 2 * s,
        )
        pygame.draw.rect(screen, (250, 230, 80), rect)


# ============================================================
# Level – komplette Verwaltung von ALLEM im Spielfeld
# ============================================================

class Level:
    def __init__(self, tile_size: int):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.tile_size = tile_size

        # 2D-Array aus Tiles
        self.tiles: list[list[Tile]] = [
            [Tile(TileType.SOLID) for _ in range(self.rows)]
            for _ in range(self.cols)
        ]

        # Timer
        self.timer = BafoegTimer(BAFOEG_TIME_SECONDS)

        # Inhalte
        self.ects_items: list[ECTS] = []
        self.powerups: list[PowerUp] = []
        self.professors: list[ProfessorEnemy] = []

        # Status
        self.collected_ects = 0
        self.required_ects = REQUIRED_ECTS
        self.is_game_over = False
        self.is_won = False
        self.game_over_reason: str = ""
        self.last_powerup_message: Optional[str] = None

        # Welt erzeugen
        self._build_world()

    # --------------------------------------------------------
    # Praktische Properties
    # --------------------------------------------------------
    @property
    def is_finished(self) -> bool:
        """True, wenn Level zu Ende ist (egal ob Sieg, GameOver oder Zeit 0)."""
        return self.is_game_over or self.is_won or self.timer.is_over

    # --------------------------------------------------------
    # Welt generieren
    # --------------------------------------------------------
    def _build_world(self) -> None:
        """
        Erstes, simples Level:
         - alles erst SOLID
         - kleiner Starttunnel
         - ECTS & PowerUps auf SOLID-Feldern
         - Profs auf EMPTY-Feldern (Tunneln)
        """
        # alles SOLID
        for x in range(self.cols):
            for y in range(self.rows):
                self.tiles[x][y].type = TileType.SOLID

        # Start-Korridor ungefähr links oben
        self.tiles[1][1].dig()
        self.tiles[1][2].dig()
        self.tiles[2][2].dig()

        # ---------------- ECTS verteilen ----------------
        ects_positions: set[tuple[int, int]] = set()
        while len(ects_positions) < self.required_ects:
            x = random.randrange(self.cols)
            y = random.randrange(self.rows)
            if (x, y) == (1, 1):
                continue
            if self.tiles[x][y].is_solid:
                ects_positions.add((x, y))

        for (x, y) in ects_positions:
            self.ects_items.append(ECTS(x, y, self.tile_size))

        # ---------------- PowerUps verteilen -------------
        candidates = list(ects_positions)
        random.shuffle(candidates)
        for (x, y) in candidates[: max(1, self.required_ects // 2)]:
            ptype = random.choice(list(PowerUpType))
            self.powerups.append(PowerUp(x, y, self.tile_size, ptype))

      # ---------------- Professoren erzeugen ----------------------
        for prof_info in PROFESSORS:
            img_path = prof_info["sprite"]
            qlist = prof_info["questions"]

            sprite = Sprite(img_path, self.tile_size, self.tile_size)

    # Prof darf ÜBERALL spawnen — egal ob Block oder Tunnel.
    # Bedingungen:
    #   - NICHT auf dem Startfeld (1,1)
    #   - NICHT auf einem bereits besetzten Feld (kein zweiter Prof dort)
            while True:
                x = random.randrange(self.cols)
                y = random.randrange(self.rows)

        # nicht auf Spielerstart
                if (x, y) == (1, 1):
                    continue

        # nicht doppelt besetzen
                if any(p.grid_x == x and p.grid_y == y for p in self.professors):
                    continue

                prof = ProfessorEnemy(x, y, self.tile_size, sprite, qlist)
                self.professors.append(prof)
                break


    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cols and 0 <= y < self.rows

    def dig(self, x: int, y: int) -> None:
        """Einfacher Wrapper um Tile.dig()."""
        self.tiles[x][y].dig()

    # --------------------------------------------------------
    # Update pro Frame
    # --------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.is_finished:
            return

        self.timer.update(dt)
        if self.timer.is_over and not self.is_won:
            self.is_game_over = True
            self.game_over_reason = "BAföG-Zeit abgelaufen."

        # Professoren bewegen
        for prof in self.professors:
            prof.update(dt, self)

    # --------------------------------------------------------
    # Wenn der Spieler ein Feld betritt
    # --------------------------------------------------------
    def on_player_enter_tile(self, gx: int, gy: int, student) -> Optional[ProfessorEnemy]:
        """
        Wird von Student.move() aufgerufen, nachdem die Position aktualisiert wurde.

        Hier kümmern wir uns um:
          - ECTS einsammeln
          - PowerUps aktivieren
          - Prüfen, ob genug ECTS für Sieg
          - Prüfen, ob auf diesem Feld ein Prof steht
        """
        touched_prof: Optional[ProfessorEnemy] = None

        # --- ECTS sammeln ---
        for ects in list(self.ects_items):
            if ects.gx == gx and ects.gy == gy:
                self.ects_items.remove(ects)
                self.collected_ects += 1

        # Sieg prüfen
        if self.collected_ects >= self.required_ects and not self.is_game_over:
            self.is_won = True

        # --- PowerUps aktivieren ---
        for p in list(self.powerups):
            if p.grid_x == gx and p.grid_y == gy:
                self.powerups.remove(p)
                msg = p.apply_to(self, student)
                if msg:
                    self.last_powerup_message = msg

        # --- Professoren checken ---
        for prof in self.professors:
            if prof.grid_x == gx and prof.grid_y == gy:
                touched_prof = prof
                break

        return touched_prof
    
    def get_question_for_prof(self, prof: ProfessorEnemy) -> dict:
        """
        Wird vom Game aufgerufen, sobald wir auf einem Professor stehen.

        Vorteil: Das Level muss nicht wissen, welche Art Professor das ist –
        der Professor selbst kennt seine Fragenliste und liefert einfach
        eine Frage zurück.
        """
        return prof.get_question()


    # --------------------------------------------------------
    # Zeichnen
    # --------------------------------------------------------
    def draw(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
        block_solid,
        block_empty,
    ) -> None:
        """Grid + ECTS + PowerUps + Profs zeichnen."""

        # Grid
        for x in range(self.cols):
            for y in range(self.rows):
                tile = self.tiles[x][y]
                px = offset_x + x * self.tile_size
                py = offset_y + y * self.tile_size

                if tile.is_solid:
                    block_solid.draw(screen, px, py)
                else:
                    block_empty.draw(screen, px, py)

        # ECTS
        for ects in self.ects_items:
            ects.draw(screen, offset_x, offset_y)

        # PowerUps
        for p in self.powerups:
            p.draw(screen, offset_x, offset_y)

        # Professoren
        for prof in self.professors:
            prof.draw(screen, offset_x, offset_y)
