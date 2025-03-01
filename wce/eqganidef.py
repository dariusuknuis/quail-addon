# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqganidef:
	@staticmethod
	def definition():
		return "EQGANIDEF"

	tag:str
	version:int
	strict:int

	class bone:
		bone:str


		class frame:

			milliseconds:int

			translation:tuple[float, float, float]

			rotation:tuple[float, float, float, float]

			scale:tuple[float, float, float]

		frames:list[frame]

	bones:list[bone]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "STRICT", 1)
		self.strict = int(records[1])
		records = property(r, "NUMBONES", 1)
		numbones = int(records[1])

		self.bones = []
		for i in range(numbones):
			bonei = self.bone()
			records = property(r, "BONE", 1)
			bonei.bone = str(records[1])
			records = property(r, "NUMFRAMES", 1)
			numframes = int(records[1])

			bonei.frames = []
			for j in range(numframes):
				framej = self.bone.frame()
				property(r, "FRAME", 0)

				records = property(r, "MILLISECONDS", 1)
				framej.milliseconds = int(records[1])
				records = property(r, "TRANSLATION", 3)
				framej.translation = float(records[1]), float(records[2]), float(records[3])
				records = property(r, "ROTATION", 4)
				framej.rotation = float(records[1]), float(records[2]), float(records[3]), float(records[4])
				records = property(r, "SCALE", 3)
				framej.scale = float(records[1]), float(records[2]), float(records[3])
				bonei.frames.append(framej)
			self.bones.append(bonei)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tSTRICT \"{self.strict}\"\n")
		w.write(f"\tNUMBONES \"{len(self.bones)}\"\n")
		for bonei in self.bones:
			w.write(f"\t\tBONE \"{bonei.bone}\"\n")
			w.write(f"\t\tNUMFRAMES \"{len(bonei.frames)}\"\n")
			for framej in bonei.frames:
				w.write(f"\t\t\tFRAME\n")
				w.write(f"\t\t\tMILLISECONDS \"{framej.milliseconds}\"\n")
				w.write(f"\t\t\tTRANSLATION \"{framej.translation}\"\n")
				w.write(f"\t\t\tROTATION \"{framej.rotation}\"\n")
				w.write(f"\t\t\tSCALE \"{framej.scale}\"\n")

