# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgloddef:
	@staticmethod
	def definition():
		return "EQGLODDEF"

	tag:str

	def __init__(self):
		self.tag = ""
		self.lods = []

	class lod:

		def __init__(self):
			self.lod = self.lod()

		class lod:
			tag:str
			category:str
			distance:float

			def __init__(self):
				self.tag = "" #4
				self.category = "" #4
				self.distance = 0.0 #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NUMLODS", 1)
		numlods = int(records[1])

		self.lods = []
		for i in range(numlods):
			lodi = type(self).lod()
			property(r, "LOD", 0)

			records = property(r, "TAG", 1)
			lodi.lod.tag = str(records[1])
			records = property(r, "CATEGORY", 1)
			lodi.lod.category = str(records[1])
			records = property(r, "DISTANCE", 1)
			lodi.lod.distance = float(records[1])
			self.lods.append(lodi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMLODS \"{len(self.lods)}\"\n")
		for lodi in self.lods:
			w.write(f"\t\tLOD\n")
			w.write(f"\t\t\tTAG \"{lodi.lod.tag}\"\n")
			w.write(f"\t\t\tCATEGORY \"{lodi.lod.category}\"\n")
			w.write(f"\t\t\tDISTANCE \"{lodi.lod.distance}\"\n")
		return ""

