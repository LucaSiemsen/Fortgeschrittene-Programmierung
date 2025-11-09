# ============================================================
# collectibles.py – Sammelobjekt-Basis + ECTS
# ECTS: Erhöht den Level-Fortschritt (collectedECTS).
# ============================================================

from abc import ABC, abstractmethod

class Collectible(ABC):
    @abstractmethod
    def onPickUp(self, student) -> None:
        """Wird ausgelöst, wenn der Student einsammelt."""
        ...

class ECTS(Collectible):
    def __init__(self, value: int = 1):
        self.value = value

    def onPickUp(self, student) -> None:
        # kleiner Shortcut: Student kennt sein aktuelles Level über Callback
        if hasattr(student, "on_gain_ects"):
            student.on_gain_ects(self.value)
