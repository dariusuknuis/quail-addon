# NOT generated — custom helper class

import io

class track:
    def __init__(self):
        # ----------------------------------------
        # Identity
        # ----------------------------------------
        self.tag: str = ""              # TRACKINSTANCE tag
        self.trackdef: str = ""         # TRACKDEFINITION tag

        # ----------------------------------------
        # Instance properties
        # ----------------------------------------
        self.interpolate: int = 0
        self.reverse: int = 0
        self.sleep: int | None = None

        # ----------------------------------------
        # Definition data
        # ----------------------------------------
        self.frames: list[tuple[int,int,int,int,int,int,int,int]] = []
        self.legacyframes: list[tuple[int,int,int,int,float,float,float,float]] = []

        # ----------------------------------------
        # Extra metadata (NOT written)
        # ----------------------------------------
        self.animation: str = ""   # e.g. "C01_AVI"
        self.is_pose: bool = False

    # ----------------------------------------
    # Write BOTH definition + instance
    # ----------------------------------------
    def write(self, w: io.TextIOWrapper) -> str:

        # ----------------------------------------
        # TRACKDEFINITION
        # ----------------------------------------
        w.write(f'TRACKDEFINITION "{self.trackdef}"\n')

        w.write(f"\tNUMFRAMES {len(self.frames)}\n")
        for f in self.frames:
            w.write(
                f"\t\tFRAME {f[0]} {f[1]} {f[2]} {f[3]} "
                f"{f[4]} {f[5]} {f[6]} {f[7]}\n"
            )

        w.write(f"\tNUMLEGACYFRAMES {len(self.legacyframes)}\n")
        for lf in self.legacyframes:
            w.write(
                f"\t\tLEGACYFRAME {lf[0]} {lf[1]} {lf[2]} {lf[3]} "
                f"{format(lf[4], '.8e')} {format(lf[5], '.8e')} "
                f"{format(lf[6], '.8e')} {format(lf[7], '.8e')}\n"
            )

        w.write("\n")

        # ----------------------------------------
        # TRACKINSTANCE
        # ----------------------------------------
        w.write(f'TRACKINSTANCE "{self.tag}"\n')
        w.write(f'\tTRACKDEF "{self.trackdef}"\n')
        w.write(f"\tINTERPOLATE {self.interpolate}\n")
        w.write(f"\tREVERSE {self.reverse}\n")
        w.write(f"\tSLEEP? {('NULL' if self.sleep is None else self.sleep)}\n")

        return ""