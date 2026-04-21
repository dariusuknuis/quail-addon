# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgparticlepointdef:
	@staticmethod
	def definition():
		return "EQGPARTICLEPOINTDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.points = []

	class point:
		point:str
		bonename:str
		translation:tuple[float, float, float]
		rotation:tuple[float, float, float]
		scale:tuple[float, float, float]

		def __init__(self):
			self.point = "" #3
			self.bonename = "" #3
			self.translation = (0.0, 0.0, 0.0) #3
			self.rotation = (0.0, 0.0, 0.0) #3
			self.scale = (0.0, 0.0, 0.0) #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMPOINTS", 1)
		numpoints = int(records[1])

		self.points = []
		for i in range(numpoints):
			pointi = type(self).point()
			records = property(r, "POINT", 1)
			pointi.point = str(records[1])
			records = property(r, "BONENAME", 1)
			pointi.bonename = str(records[1])
			records = property(r, "TRANSLATION", 3)
			pointi.translation = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "ROTATION", 3)
			pointi.rotation = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "SCALE", 3)
			pointi.scale = (float(records[1]), float(records[2]), float(records[3]))
			self.points.append(pointi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMPOINTS \"{len(self.points)}\"\n")
		for pointi in self.points:
			w.write(f"\t\tPOINT \"{pointi.point}\"\n")
			w.write(f"\t\tBONENAME \"{pointi.bonename}\"\n")
			w.write(f"\t\tTRANSLATION {pointi.translation[0]} {pointi.translation[1]} {pointi.translation[2]}\n")
			w.write(f"\t\tROTATION {pointi.rotation[0]} {pointi.rotation[1]} {pointi.rotation[2]}\n")
			w.write(f"\t\tSCALE {pointi.scale[0]} {pointi.scale[1]} {pointi.scale[2]}\n")
		return ""

