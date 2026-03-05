# Generated from quail, DO NOT EDIT
import io
from .parse import property

class polyhedrondefinition:
	@staticmethod
	def definition():
		return "POLYHEDRONDEFINITION"

	tag:str
	boundingradius:float
	scalefactor:float
	hexoneflag:int

	def __init__(self):
		self.tag = ""
		self.boundingradius = 0.0 #2
		self.scalefactor = 0.0 #2
		self.hexoneflag = 0 #2
		self.vertices = []
		self.faces = []

	class xyz:
		xyz:tuple[float, float, float]

		def __init__(self):
			self.xyz = tuple[float, float, float] #3

	class vertexlist:
		vertexlist:list[str]

		def __init__(self):
			self.vertexlist = list[str] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = property(r, "SCALEFACTOR", 1)
		self.scalefactor = float(records[1])
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			xyzi = type(self).xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.vertices.append(xyzi)
		records = property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.faces = []
		for i in range(numfaces):
			vertexlisti = type(self).vertexlist()
			records = property(r, "VERTEXLIST", -1)
			vertexlisti.vertexlist = records[1:]

			self.faces.append(vertexlisti)
		records = property(r, "HEXONEFLAG", 1)
		self.hexoneflag = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tBOUNDINGRADIUS \"{self.boundingradius}\"\n")
		w.write(f"\tSCALEFACTOR \"{self.scalefactor}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.vertices)}\"\n")
		for xyzi in self.vertices:
			w.write(f"\t\tXYZ \"{xyzi.xyz}\"\n")
		w.write(f"\tNUMFACES \"{len(self.faces)}\"\n")
		for vertexlisti in self.faces:
			w.write(f"\t\tVERTEXLIST \"{vertexlisti.vertexlist}\"\n")
		w.write(f"\tHEXONEFLAG \"{self.hexoneflag}\"\n")
		return ""

