# ============================================================
# powerups.py – PowerUp-Basis + konkrete Effekte
# EnergyDrink: nächste Antwort automatisch (answersBuffer += 1)
# ChatGPT: Klausur nur 1 Antwort (hier als Flag am Student)
# Pizza: 1x Rettung (Flag) + optionaler Slowdown (später)
# Party: 50/50 invuln (5s) oder stun (5s)
# ============================================================

import random
import time
from .collectibles import Collectible

class PowerUp(Collectible):
    def applyTo(self, student) -> None:
        raise NotImplementedError

    def onPickUp(self, student) -> None:
        self.applyTo(student)

class EnergyDrink(PowerUp):
    def applyTo(self, student) -> None:
        student.answersBuffer = min(3, getattr(student, "answersBuffer", 0) + 1)

class ChatGPT(PowerUp):
    def applyTo(self, student) -> None:
        # Einfaches Flag – Auswertung später in der Kampf-Logik
        student.chatgptBoostUntil = time.time() + 10.0  # 10s „Boost“

class Pizza(PowerUp):
    def applyTo(self, student) -> None:
        student.hasPizzaShield = True
        # Optional: Slowdown nach Rettung wird später aktiviert.

class Party(PowerUp):
    def applyTo(self, student) -> None:
        now = time.time()
        if random.random() < 0.5:
            student.invulnerableUntil = max(getattr(student, "invulnerableUntil", 0.0), now + 5.0)
        else:
            student.stunnedUntil = max(getattr(student, "stunnedUntil", 0.0), now + 5.0)
