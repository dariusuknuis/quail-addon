# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgparticlepointdef:
	@staticmethod
	def definition():
		return "EQGPARTICLEPOINTDEF"

	tag:str
	version:int

	class point:
		point:str

		bonename:str

		translation:tuple[float, float, float]

		rotation:tuple[float, float, float]

		scale:tuple[float, float, float]

	points:list[point]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMPOINTS", 1)
		numpoints = int(records[1])

		self.points = []
		for i in range(numpoints):
			pointi = self.point()
			records = property(r, "POINT", 1)
			pointi.point = str(records[1])
			records = property(r, "BONENAME", 1)
			pointi.bonename = str(records[1])
			records = property(r, "TRANSLATION", 3)
			pointi.translation = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "ROTATION", 3)
			pointi.rotation = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "SCALE", 3)
			pointi.scale = float(records[1]), float(records[2]), float(records[3])
			self.points.append(pointi)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMPOINTS \"{len(self.points)}\"\n")
		for pointi in self.points:
			w.write(f"\t\tPOINT \"{pointi.point}\"\n")
			w.write(f"\t\tBONENAME \"{pointi.bonename}\"\n")
			w.write(f"\t\tTRANSLATION \"{pointi.translation}\"\n")
			w.write(f"\t\tROTATION \"{pointi.rotation}\"\n")
			w.write(f"\t\tSCALE \"{pointi.scale}\"\n")

