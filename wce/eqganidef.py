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

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.strict = 0 #2
		self.bones = []

	class bone:
		bone:str

		def __init__(self):
			self.bone = "" #3
			self.frames = []

		class frame:
			milliseconds:int
			translation:tuple[float, float, float]
			rotation:tuple[float, float, float, float]
			scale:tuple[float, float, float]

			def __init__(self):
				self.milliseconds = 0 #4
				self.translation = tuple[float, float, float] #4
				self.rotation = tuple[float, float, float, float] #4
				self.scale = tuple[float, float, float] #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "STRICT", 1)
		self.strict = int(records[1])
		records = property(r, "NUMBONES", 1)
		numbones = int(records[1])

		self.bones = []
		for i in range(numbones):
			bonei = type(self).bone()
			records = property(r, "BONE", 1)
			bonei.bone = str(records[1])
			records = property(r, "NUMFRAMES", 1)
			numframes = int(records[1])

			bonei.frames = []
			for j in range(numframes):
				framej = type(bonei).frame()
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
		return ""

	def write(self, w:io.TextIOWrapper)->str:
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
		return ""

