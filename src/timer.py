# ============================================================
# timer.py – BAföG-Countdown für das Spiel
# ------------------------------------------------------------
# Kleine Hilfsklasse, die die verbleibende BAföG-Zeit trackt.
# Extrem simpel gehalten, damit sie überall eingesetzt werden kann.
# ============================================================

class BafoegTimer:
    """Ein sehr einfacher Countdown-Timer."""

    def __init__(self, duration_seconds: float):
        # Wie viele Sekunden man insgesamt bekommt
        self.duration = duration_seconds
        # Wie viele Sekunden aktuell übrig sind
        self.time_left = duration_seconds

    def reset(self) -> None:
        """Timer vollständig zurücksetzen."""
        self.time_left = self.duration

    def update(self, dt: float) -> None:
        """
        Zeit verringern.
        
        dt = vergangene Zeit in Sekunden seit letztem Frame.
        """
        self.time_left = max(0.0, self.time_left - dt)

    @property
    def is_over(self) -> bool:
        """Ist die Zeit abgelaufen?"""
        return self.time_left <= 0.0
