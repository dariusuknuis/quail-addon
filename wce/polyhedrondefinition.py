# Generated from quail, DO NOT EDIT
import io
from .parse import property

class polyhedrondefinition:
	@staticmethod
	def definition():
		return "POLYHEDRONDEFINITION"

	tag:str
	boundingradius:float
	scalefactor:float | None

	def __init__(self):
		self.tag = ""
		self.boundingradius = 0.0 #2
		self.scalefactor = None #2
		self.vertices = []
		self.faces = []

	class xyz:
		xyz:tuple[float, float, float]

		def __init__(self):
			self.xyz = (0.0, 0.0, 0.0) #3

	class vertexlist:
		vertexlist:list[str]

		def __init__(self):
			self.vertexlist = [] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = property(r, "SCALEFACTOR?", 1)
		self.scalefactor = float(records[1]) if records[1] != "NULL" else None
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			xyzi = type(self).xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = (float(records[1]), float(records[2]), float(records[3]))
			self.vertices.append(xyzi)
		records = property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.faces = []
		for i in range(numfaces):
			vertexlisti = type(self).vertexlist()
			records = property(r, "VERTEXLIST", -1)
			vertexlisti.vertexlist = records[1:]

			self.faces.append(vertexlisti)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tBOUNDINGRADIUS {format(self.boundingradius, '.8e')}\n")
		w.write(f"\tSCALEFACTOR? {('NULL' if self.scalefactor is None else format(self.scalefactor, '.8e'))}\n")
		w.write(f"\tNUMVERTICES {len(self.vertices)}\n")
		for xyzi in self.vertices:
			w.write(f"\t\tXYZ {format(xyzi.xyz[0], '.8e')} {format(xyzi.xyz[1], '.8e')} {format(xyzi.xyz[2], '.8e')}\n")
		w.write(f"\tNUMFACES {len(self.faces)}\n")
		for vertexlisti in self.faces:
			w.write(f"\t\tVERTEXLIST {' '.join(vertexlisti.vertexlist)}\n")
		return ""

