# ============================================================
# entities.py – Spielfiguren
# ------------------------------------------------------------
# Hier lebt aktuell nur der Student (also wir im Spiel).
# Kann:
#   - sich im Grid bewegen (ein Feld pro Tastendruck)
#   - automatisch graben, wenn noch Erde vor ihm ist
#   - merken, ob es eine offene Professorfrage gibt
# ============================================================

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .level import Level
    from .enemy import ProfessorEnemy


class Student:
    """
    Repräsentiert den Spieler im Grid.
    Der Student weiß:
      - auf welcher Grid-Position er steht (grid_x, grid_y)
      - wie groß eine Kachel ist (tile_size)
      - welches Sprite ihn darstellt
      - ob gerade eine Professorfrage offen ist
    """

    def __init__(self, grid_x: int, grid_y: int, tile_size: int, sprite: pygame.Surface):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_size = tile_size
        self.sprite = sprite

        # Frage, die gerade aktiv ist (wenn man in einen Prof läuft)
        self.pending_question = None      # kommt aus config.Question
        self.pending_professor: Optional["ProfessorEnemy"] = None

        # Status aus PowerUps (z.B. Pizza-Schild)
        self.has_pizza_shield: bool = False

    # --------------------------------------------------------
    # Hilfsfunktionen für Position im Grid / auf dem Screen
    # --------------------------------------------------------
    @property
    def pos(self) -> tuple[int, int]:
        return self.grid_x, self.grid_y

    def reset(self, grid_x: int, grid_y: int) -> None:
        """Student an andere Startposition setzen (z.B. bei Restart)."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pending_question = None
        self.pending_professor = None

    # --------------------------------------------------------
    # Bewegung & Grab-Logik
    # --------------------------------------------------------
    def move(self, dx: int, dy: int, level: "Level") -> Optional["ProfessorEnemy"]:
        """
        Ein Feld bewegen.
        - dx, dy sind -1/0/1 (Richtung)
        - das Level kümmert sich um:
            * Graben
            * ECTS einsammeln
            * PowerUps aktivieren
            * Professoren treffen
        """

        # Wenn Level schon fertig ist (gewonnen / verloren / Zeit abgelaufen),
        # keine weitere Bewegung.
        if level.is_finished:
            return None

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        # Kollision mit Spielfeldrand
        if not level.in_bounds(new_x, new_y):
            return None

        # Wenn da noch Erde ist, wird sie automatisch zu Tunnel
        if level.tiles[new_x][new_y].is_solid:
            level.dig(new_x, new_y)

        # Position tatsächlich updaten
        self.grid_x = new_x
        self.grid_y = new_y

        # Level fragen, ob wir etwas betreten haben:
        #   - ECTS
        #   - PowerUp
        #   - Professor
        prof = level.on_player_enter_tile(new_x, new_y, self)

        # Wenn wir in einen Professor gelaufen sind, merken wir uns,
        # dass jetzt eine Frage beantwortet werden muss.
        if prof is not None:
            self.pending_professor = prof
            self.pending_question = prof.get_question()

        return prof

    # --------------------------------------------------------
    # Zeichnen
    # --------------------------------------------------------
    def draw(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """
        Student an der richtigen Stelle ins Fenster zeichnen.
        offset_x/offset_y verschieben das Grid, damit es zentriert ist.
        """
        px = offset_x + self.grid_x * self.tile_size
        py = offset_y + self.grid_y * self.tile_size
        screen.blit(self.sprite, (px, py))
