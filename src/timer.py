# ============================================================
# timer.py – BAföG-Timer
# Regeln:
# - tickt runter; expired() meldet Zeitablauf.
# - Pizza kann einmal Gnade geben (graceUsed).
# ============================================================

class BafoegTimer:
    def __init__(self, seconds_left: int = 60):
        self.secondsLeft = float(seconds_left)
        self.graceUsed = False

    def tick(self, dt: float) -> None:
        self.secondsLeft = max(0.0, self.secondsLeft - dt)

    def expired(self) -> bool:
        return self.secondsLeft <= 0.0

    def applyPizzaGrace(self) -> None:
        # einfache Variante: +10s, aber nur einmal
        if not self.graceUsed:
            self.secondsLeft += 10.0
            self.graceUsed = True
