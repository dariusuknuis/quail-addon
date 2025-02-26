# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class polyhedrondefinition:
	@staticmethod
	def definition():
		return "POLYHEDRONDEFINITION"

	tag:str
	boundingradius:float
	scalefactor:float

	class xyz:
		xyz:tuple[float, float, float]

	xyzs:list[xyz]

	class vertexlist:
		vertexlist:list[str]

	vertexlists:list[vertexlist]
	hexoneflag:int

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = parse.property(r, "SCALEFACTOR", 1)
		self.scalefactor = float(records[1])
		records = parse.property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.xyzs = []
		for i in range(numvertices):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.vertexlists = []
		for i in range(numfaces):
			vertexlisti = self.vertexlist()
			records = parse.property(r, "VERTEXLIST", -1)
			vertexlisti.vertexlist = records[1:]

			self.vertexlists.append(vertexlisti)
		records = parse.property(r, "HEXONEFLAG", 1)
		self.hexoneflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tBOUNDINGRADIUS \"{self.boundingradius}\"\n")
		w.write(f"\tSCALEFACTOR \"{self.scalefactor}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"\t\tXYZ \"{xyzi.xyz}\"\n")
		w.write(f"\tNUMFACES \"{len(self.vertexlists)}\"\n")
		for vertexlisti in self.vertexlists:
			w.write(f"VERTEXLIST \"{vertexlisti.vertexlist}\"\n")
		w.write(f"\tHEXONEFLAG \"{self.hexoneflag}\"\n")

