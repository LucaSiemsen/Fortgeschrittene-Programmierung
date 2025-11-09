# ============================================================
# block.py – einfache, zerstörbare Level-Kachel
# Regel: nur Student darf zerstören; Zustand bleibt bis Levelende.
# ============================================================

class Block:
    def __init__(self, destroyed: bool = False):
        self.isDestroyed = destroyed

    def destroy(self) -> None:
        self.isDestroyed = True

    def is_passable(self) -> bool:
        # könnte später komplexer werden (versch. Typen)
        return self.isDestroyed
