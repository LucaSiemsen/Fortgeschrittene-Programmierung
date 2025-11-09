# ============================================================
# game.py – Hauptlogik von "Dig Or Exma"
# ------------------------------------------------------------
# Was hier passiert:
#  - Steuerung: EIN Feld pro Tastendruck (kein „zu weites Rutschen“)
#  - Bewegung == Graben: Wenn vor mir Erde ist, buddle ich mich rein
#  - ECTS einsammeln (HUD zählt mit)
#  - Gegner (Dozent/Klausur) als Platzhalter
#    -> Kontakt = Game Over (erstmal knallhart, später Pizza/Invuln etc.)
#  - BAföG-Timer läuft mit
#  - Zeichnen von Raster, Student, ECTS, Gegnern und HUD
# ============================================================

import pygame as pg
from .level import Level, GRID_W, GRID_H
from .entity import GridPos, Direction, TILE
from .student import Student
from .enemy import Dozent, Klausur  # Gegnertypen kommen aus enemy.py

class Game:
    def __init__(self):
        # Level 1 (ECTS-Ziel + Startzeit kann ich hier schnell tweaken)
        self.level = Level(idx=1, required_ects=2, start_time=30)

        # Student spawnt sichtbar links oben
        self.student = Student(GridPos(2, 2))
        # Callback: Wenn der Student ECTS einsackt, erhöht Game den Fortschritt
        self.student.on_gain_ects = self.gain_ects

        # Damit der Start nicht „eingemauert“ ist, mache ich das Startfeld frei
        self.level.blocks[self.student.position.x][self.student.position.y].destroy()

        # ECTS-Positionen – minimaler Demo-Spawn (passt zum Ziel 2/2)
        # (später: zufällig generieren oder aus Leveldatei laden)
        self.ects_positions = {(6, 4), (12, 8)}

        # Gegner-Spawns – rein statisch für den ersten Prototyp
        self.enemies = [
            Dozent(GridPos(8, 4)),      # „leichter“ Gegner (1 HP – hier egal)
            Klausur(GridPos(14, 10)),   # „härter“ (5 HP – hier auch egal)
        ]

        # Zustände für schöne Meldungen
        self.is_game_over = False
        self.game_over_reason = ""

    # ------------------------------------------------------------
    # Hilfsfunktion: Student-Fortschritt erhöhen
    # ------------------------------------------------------------
    def gain_ects(self, value: int) -> None:
        self.level.collectedECTS += value

    # ------------------------------------------------------------
    # Hilfsfunktion: Game Over setzen (friert Input/Logik nicht ein,
    # aber zeigt halt deutlich an, warum Schluss ist)
    # ------------------------------------------------------------
    def game_over(self, reason: str) -> None:
        self.is_game_over = True
        self.game_over_reason = reason

    # ------------------------------------------------------------
    # Kernbewegung: EIN Feld pro Tastendruck – und dabei „graben“
    # Idee: Wenn Zielfeld noch Erde hat, zerstöre es und zieh rein.
    # So fühlt sich Bewegen automatisch wie Buddeln an (klassisch).
    # ------------------------------------------------------------
    def try_step(self, direction: tuple[int, int]) -> None:
        if self.is_game_over:
            return  # Nach Game Over nichts mehr verschieben

        cx, cy = self.student.position.x, self.student.position.y
        nx = max(0, min(GRID_W - 1, cx + direction[0]))
        ny = max(0, min(GRID_H - 1, cy + direction[1]))

        # Wenn das Zielfeld noch nicht frei ist: „graben“
        target_block = self.level.blocks[nx][ny]
        if not target_block.isDestroyed:
            target_block.destroy()  # erstes Betreten räumt die Erde weg

        # Und dann reinbewegen (falls ich eh an der Kante war, bleib ich halt)
        self.student.position = GridPos(nx, ny)

        # Direkt nach dem Schritt: Kollision mit Gegnern prüfen
        self.check_enemy_contact()

    # ------------------------------------------------------------
    # Gegnerkontakt prüfen – gleiche Zelle => Game Over
    # (später: Pizza/Invulnerability hier berücksichtigen)
    # ------------------------------------------------------------
    def check_enemy_contact(self) -> None:
        for enemy in self.enemies:
            if (enemy.position.x, enemy.position.y) == (self.student.position.x, self.student.position.y):
                # Dozent vs. Klausur – einfach unterschiedliche Begründung
                if isinstance(enemy, Dozent):
                    self.game_over("Vom Dozenten erwischt.")
                else:
                    self.game_over("Bei der Klausur durchgefallen.")
                break

    # ------------------------------------------------------------
    # Hauptspielschleife
    # ------------------------------------------------------------
    def run(self):
        pg.init()
        pg.display.set_caption("Dig Or Exma – Prototyp")

        # Fenster auf Rastergröße
        W, H = GRID_W * TILE, GRID_H * TILE
        screen = pg.display.set_mode((W, H))
        clock = pg.time.Clock()
        font = pg.font.SysFont(None, 22)

        running = True
        while running:
            dt = clock.tick(60) / 1000.0  # Sekunden seit letztem Frame

            # ---------- Eingaben ----------
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    running = False

                elif e.type == pg.KEYDOWN:
                    # Graben auf dem aktuellen Feld (macht Tunnel sichtbar)
                    if e.key == pg.K_g:
                        self.level.blocks[self.student.position.x][self.student.position.y].destroy()

                    # Ein Feld pro Tastendruck – mit Auto-Buddeln ins Zielfeld
                    elif e.key == pg.K_UP:
                        self.try_step(Direction.UP)
                    elif e.key == pg.K_DOWN:
                        self.try_step(Direction.DOWN)
                    elif e.key == pg.K_LEFT:
                        self.try_step(Direction.LEFT)
                    elif e.key == pg.K_RIGHT:
                        self.try_step(Direction.RIGHT)

            # ---------- Logik ----------
            if not self.is_game_over:
                self.level.update(dt)

                # ECTS einsammeln, wenn ich drauf stehe
                pos_tuple = (self.student.position.x, self.student.position.y)
                if pos_tuple in self.ects_positions:
                    self.ects_positions.remove(pos_tuple)
                    self.gain_ects(1)

                # (Optional: wenn Level fertig ist, könnte man hier direkt next level triggern)
                # if self.level.isCleared(): self.next_level()

            # ---------- Render ----------
            screen.fill((18, 18, 24))

            # Boden / Wände (Braun = Erde, Grau = gegraben)
            for x in range(GRID_W):
                for y in range(GRID_H):
                    r = pg.Rect(x * TILE, y * TILE, TILE - 1, TILE - 1)
                    color = (100, 70, 40) if not self.level.blocks[x][y].isDestroyed else (60, 60, 60)
                    pg.draw.rect(screen, color, r)

            # ECTS – kleine gelbe Kästchen
            for ex, ey in self.ects_positions:
                pg.draw.rect(screen, (240, 200, 60),
                             pg.Rect(ex * TILE + 4, ey * TILE + 4, TILE - 8, TILE - 8))

            # Gegner – rot (Dozent) und dunkelrot (Klausur), nur als Platzhalter
            for enemy in self.enemies:
                col = (220, 80, 80) if isinstance(enemy, Dozent) else (180, 40, 40)
                pg.draw.rect(screen, col,
                             pg.Rect(enemy.position.x * TILE, enemy.position.y * TILE, TILE - 2, TILE - 2))

            # Student – grün
            pg.draw.rect(screen, (50, 220, 90),
                         pg.Rect(self.student.position.x * TILE, self.student.position.y * TILE, TILE - 2, TILE - 2))

            # HUD
            hud = font.render(
                f"Zeit: {int(self.level.timer.secondsLeft)}s   "
                f"ECTS: {self.level.collectedECTS}/{self.level.requiredECTS}",
                True, (230, 230, 230)
            )
            screen.blit(hud, (8, 6))

            # Zustandsmeldungen (freundlich, damit man weiß, was passiert ist)
            if self.is_game_over:
                msg = font.render(f"Game Over – {self.game_over_reason}", True, (255, 120, 120))
                screen.blit(msg, (W // 2 - 150, H // 2))
            elif self.level.isCleared():
                msg = font.render("Level geschafft! 🎓", True, (120, 255, 120))
                screen.blit(msg, (W // 2 - 110, H // 2))

            pg.display.flip()

        pg.quit()
