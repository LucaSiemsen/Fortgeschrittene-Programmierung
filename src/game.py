# game.py
# ----------------------------------------------------------
# Game-Controller:
#  - kümmert sich um Menü, Spiel, Frage-Dialoge
#  - hält Level, Student und rendert alles
# ----------------------------------------------------------

from __future__ import annotations

import sys
from enum import Enum, auto

import pygame

from .config import (
    GRID_COLS,
    GRID_ROWS,
    GRID_MARGIN_X_TILES,
    GRID_MARGIN_Y_TILES,
    REQUIRED_ECTS,
)
from .graphics import Sprite
from .entities import Student
from .level import Level



class GameState(Enum):
    MENU = auto()
    RUNNING = auto()
    QUESTION = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()


class Game:
    def __init__(self):
        pygame.init()

        # Vollbild-Fenster
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.info = pygame.display.Info()
        self.width, self.height = self.info.current_w, self.info.current_h
        pygame.display.set_caption("Dig Or Exma – Team 23")

        self.clock = pygame.time.Clock()

        # Tile-Größe anhand der Bildschirmgröße bestimmen
        max_tile_w = self.width // (GRID_COLS + 2 * GRID_MARGIN_X_TILES)
        max_tile_h = self.height // (GRID_ROWS + 2 * GRID_MARGIN_Y_TILES)
        self.tile_size = min(max_tile_w, max_tile_h)

        # Offset, damit das Grid zentriert ist
        self.grid_offset_x = (self.width - GRID_COLS * self.tile_size) // 2
        self.grid_offset_y = (self.height - GRID_ROWS * self.tile_size) // 2

        # Hintergrundbild
        bg = pygame.image.load("assets/sprites/Background.png").convert()
        self.background = pygame.transform.scale(bg, (self.width, self.height))

        # Blöcke (Boden / Tunnel)
        self.block_solid = Sprite(
            "assets/sprites/Buchblock-1.png", self.tile_size, self.tile_size
        )
        self.block_empty = Sprite(
            "assets/sprites/leerer block.png", self.tile_size, self.tile_size
        )

        # Student-Sprite
        student_img = pygame.image.load("assets/sprites/student.png").convert_alpha()
        student_img = pygame.transform.scale(
            student_img, (self.tile_size, self.tile_size)
        )

        # Fonts
        self.font_small = pygame.font.SysFont(None, 26)
        self.font_big = pygame.font.SysFont(None, 48)
        self.font_title = pygame.font.SysFont(None, 64)

        # Game-Objekte
        self.state = GameState.MENU
        self.level: Level | None = None
        self.student: Student | None = None

        # Frage-Dialog
        self.active_prof = None
        self.active_question = None
        self.last_question_feedback: str | None = None

        # Student-Instanz anlegen (Startposition im Grid)
        self._create_level_and_student()

    # ------------------------------------------------------
    # Setup
    # ------------------------------------------------------

    def _create_level_and_student(self) -> None:
        self.level = Level(self.tile_size)
        # Startposition links oben im Tunnel (gefühlt „von oben ins Level“)
        start_x, start_y = 1, 1
        student_img = pygame.image.load("assets/sprites/student.png").convert_alpha()
        student_img = pygame.transform.scale(
            student_img, (self.tile_size, self.tile_size)
        )
        self.student = Student(start_x, start_y, self.tile_size, student_img)
        # Startfeld freigraben
        self.level.tiles[start_x][start_y].dig()

    def restart(self) -> None:
        self._create_level_and_student()
        self.state = GameState.RUNNING
        self.last_question_feedback = None

    # ------------------------------------------------------
    # Hauptschleife
    # ------------------------------------------------------

    def run(self) -> None:
        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0  # Sekunden seit letztem Frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    self.handle_key(event.key)

            # Logik-Update
            if self.state == GameState.RUNNING and self.level is not None:
                self.level.update(dt)
                if self.level.is_game_over:
                    self.state = GameState.GAME_OVER
                elif self.level.is_won:
                    self.state = GameState.LEVEL_COMPLETE

            # Zeichnen
            self.draw()

        pygame.quit()
        sys.exit()

    # ------------------------------------------------------
    # Input
    # ------------------------------------------------------

    def handle_key(self, key: int) -> None:
        if self.state == GameState.MENU:
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.restart()
        elif self.state == GameState.RUNNING:
            assert self.level is not None and self.student is not None

            if key == pygame.K_r:
                self.restart()
                return

            dx, dy = 0, 0
            if key == pygame.K_UP:
                dy = -1
            elif key == pygame.K_DOWN:
                dy = 1
            elif key == pygame.K_LEFT:
                dx = -1
            elif key == pygame.K_RIGHT:
                dx = 1

            if dx != 0 or dy != 0:
                prof = self.student.move(dx, dy, self.level)
                if prof is not None:
                    self.open_question(prof)

        elif self.state == GameState.QUESTION:
            # Antwortauswahl: 1/2/3
            if key in (pygame.K_1, pygame.K_2, pygame.K_3):
                answer_index = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[key]
                self.resolve_question(answer_index)

        elif self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            if key == pygame.K_r:
                self.restart()
            elif key in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = GameState.MENU

    # ------------------------------------------------------
    # Frage-Dialog
    # ------------------------------------------------------

    def open_question(self, prof) -> None:
        assert self.level is not None
        question = self.level.get_question_for_prof(prof)
        if question is None:
            return
        self.active_prof = prof
        self.active_question = question
        self.state = GameState.QUESTION
        self.last_question_feedback = None

    def resolve_question(self, given_index: int) -> None:
        assert self.level is not None and self.active_prof is not None
        q = self.active_question
        if q is None:
            self.state = GameState.RUNNING
            return

        if given_index == q.correct:
            # richtige Antwort => 2 ECTS als Belohnung
            self.level.collected_ects += 2
            self.last_question_feedback = (
                "Richtige Antwort! +2 ECTS. " + q.explanation
            )
            # Professor verschwindet aus dem Level
            self.level.remove_professor(self.active_prof)
        else:
            # falsche Antwort => Zeitstrafe
            self.level.timer.time_left = max(
                5.0, self.level.timer.time_left - 10.0
            )
            self.last_question_feedback = (
                "Nicht ganz richtig... -10s BAföG-Zeit. " + q.explanation
            )

        # Aufräumen
        self.active_prof = None
        self.active_question = None

        # Siegbedingung könnte durch ECTS gestiegen sein
        if self.level.collected_ects >= REQUIRED_ECTS and not self.level.is_game_over:
            self.level.is_won = True
            self.state = GameState.LEVEL_COMPLETE
        else:
            self.state = GameState.RUNNING

    # ------------------------------------------------------
    # Rendering
    # ------------------------------------------------------

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        if self.state == GameState.MENU:
            self.draw_menu()
        else:
            assert self.level is not None and self.student is not None
            self.draw_game()

        pygame.display.flip()

    def draw_menu(self) -> None:
        title = self.font_title.render("Dig Or Exma", True, (255, 255, 255))
        subtitle = self.font_small.render(
            "Ein Student, fünf ECTS und ein gnadenloser BAföG-Timer.",
            True,
            (230, 230, 230),
        )
        hint = self.font_small.render(
            "LEERTASTE / ENTER: Starten   |   ESC: Beenden",
            True,
            (230, 230, 230),
        )
        cx = self.width // 2
        cy = self.height // 2
        self.screen.blit(title, title.get_rect(center=(cx, cy - 80)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(cx, cy - 30)))
        self.screen.blit(hint, hint.get_rect(center=(cx, cy + 40)))

    def draw_game(self) -> None:
        assert self.level is not None and self.student is not None

        # Grid/Blöcke
        for x in range(self.level.cols):
            for y in range(self.level.rows):
                tile = self.level.tiles[x][y]
                px = self.grid_offset_x + x * self.tile_size
                py = self.grid_offset_y + y * self.tile_size
                rect = pygame.Rect(px, py, self.tile_size - 1, self.tile_size - 1)
                if tile.is_solid:
                    # braune "Buch-Erde"
                    pygame.draw.rect(self.screen, (100, 70, 40), rect)
                    self.block_solid.draw(self.screen, px, py)
                else:
                    # freier Tunnel
                    pygame.draw.rect(self.screen, (60, 60, 60), rect)
                    self.block_empty.draw(self.screen, px, py)

        # ECTS
        for ects in self.level.ects_items:
            ects.draw(self.screen, self.grid_offset_x, self.grid_offset_y)

        # Professoren
        for prof in self.level.professors:
            prof.draw(self.screen, self.grid_offset_x, self.grid_offset_y)

        # Student
        self.student.draw(self.screen, self.grid_offset_x, self.grid_offset_y)

        # HUD
        self.draw_hud()

        # ggf. Frage-Overlay / GameOver-Overlay
        if self.state == GameState.QUESTION:
            self.draw_question_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_center_message(
                "Game Over",
                self.level.game_over_reason,
                "R: Neustart   |   ENTER: Zurück ins Menü",
                (255, 120, 120),
            )
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_center_message(
                "Level geschafft! 🎓",
                "Du hast genug ECTS gesammelt.",
                "R: Neustart   |   ENTER: Zurück ins Menü",
                (120, 255, 120),
            )

    def draw_hud(self) -> None:
        assert self.level is not None
        hud = self.font_small.render(
            f"Zeit: {int(self.level.timer.time_left)}s   "
            f"ECTS: {self.level.collected_ects}/{REQUIRED_ECTS}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(hud, (20, 20))

        controls = self.font_small.render(
            "Pfeiltasten: bewegen/graben   |   R: Restart   |   ESC: Beenden",
            True,
            (255, 255, 255),
        )
        self.screen.blit(controls, (20, 50))

        if self.last_question_feedback:
            msg = self.font_small.render(
                self.last_question_feedback, True, (200, 255, 200)
            )
            self.screen.blit(msg, (20, self.height - 40))

    def draw_question_overlay(self) -> None:
        assert self.active_question is not None

        # halbtransparenter dunkler Hintergrund
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        q = self.active_question
        lines = [q.text] + [
            f"{i+1}) {ans}" for i, ans in enumerate(q.answers)
        ]
        lines.append("Wähle mit 1 / 2 / 3")

        cx = self.width // 2
        cy = self.height // 2 - 80

        for i, text in enumerate(lines):
            surf = self.font_small.render(text, True, (255, 255, 255))
            self.screen.blit(surf, surf.get_rect(center=(cx, cy + i * 30)))

    def draw_center_message(
        self,
        title: str,
        line1: str,
        line2: str,
        color_title: tuple[int, int, int],
    ) -> None:
        cx = self.width // 2
        cy = self.height // 2
        surf_title = self.font_big.render(title, True, color_title)
        surf_line1 = self.font_small.render(line1, True, (255, 255, 255))
        surf_line2 = self.font_small.render(line2, True, (255, 255, 255))
        self.screen.blit(surf_title, surf_title.get_rect(center=(cx, cy - 40)))
        self.screen.blit(surf_line1, surf_line1.get_rect(center=(cx, cy)))
        self.screen.blit(surf_line2, surf_line2.get_rect(center=(cx, cy + 30)))
