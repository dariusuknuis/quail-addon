# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class dmspritedef2:
	@staticmethod
	def definition():
		return "DMSPRITEDEF2"

	tag:str
	tagindex:int # The index of the tag
	centeroffset:tuple[float, float, float] # The center offset of the sprite

	class xyz:
		xyz:tuple[float, float, float] # The coordinates of a vertex

	xyzs:list[xyz]

	class uv:
		uv:tuple[float, float] # UV entry

	uvs:list[uv]

	class xyz:
		xyz:tuple[float, float, float] # The coordinates of a texture normal

	xyzs:list[xyz]

	class rgba:
		rgba:tuple[int, int, int, int] # The coordinates of a vertex

	rgbas:list[rgba]
	skinassignmentgroups:tuple[list[str]] # The skin assignment groups
	materialpalette:str # The material palette used by the sprite
	dmtrackinst:str # The DM track instance
	polyhedron:str # The polyhedron definition
	definition:str # The definition reference

	class dmface2:

		passable:int # Is face passable?

		triangle:tuple[int, int, int] # Triangle indexes

	dmface2s:list[dmface2]

	class meshop:
		meshop:tuple[int, int, float, int, int] # A mesh operation

	meshops:list[meshop]
	facematerialgroups:tuple[int, int, int] # The face material groups
	vertexmaterialgroups:tuple[int, int, int] # The vertex material groups
	boundingboxmin:tuple[float, float, float] # The minimum bounding box coordinates
	boundingboxmax:tuple[float, float, float] # The maximum bounding box coordinates
	boundingradius:float # The bounding radius of the sprite
	fpscale:int # The FPS scale of the sprite
	hexoneflag:int # The hex one flag
	hextwoflag:int # The hex two flag
	hexfourthousandflag:int # The hex four thousand flag
	hexeightthousandflag:int # The hex eight thousand flag
	hextenthousandflag:int # The hex ten thousand flag
	hextwentythousandflag:int # The hex twenty thousand flag

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "CENTEROFFSET", 3)
		self.centeroffset = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.xyzs = []
		for i in range(numvertices):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMUVS", 1)
		numuvs = int(records[1])

		self.uvs = []
		for i in range(numuvs):
			uvi = self.uv()
			records = parse.property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.uvs.append(uvi)
		records = parse.property(r, "NUMVERTEXNORMALS", 1)
		numvertexnormals = int(records[1])

		self.xyzs = []
		for i in range(numvertexnormals):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMVERTEXCOLORS", 1)
		numvertexcolors = int(records[1])

		self.rgbas = []
		for i in range(numvertexcolors):
			rgbai = self.rgba()
			records = parse.property(r, "RGBA", 4)
			rgbai.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			self.rgbas.append(rgbai)
		records = parse.property(r, "SKINASSIGNMENTGROUPS", -1)
		self.skinassignmentgroups = records[1:]

		records = parse.property(r, "MATERIALPALETTE", 1)
		self.materialpalette = str(records[1])
		records = parse.property(r, "DMTRACKINST", 1)
		self.dmtrackinst = str(records[1])
		records = parse.property(r, "POLYHEDRON", 1)
		self.polyhedron = str(records[1])
		records = parse.property(r, "DEFINITION", 1)
		self.definition = str(records[1])
		records = parse.property(r, "NUMFACE2S", 1)
		numface2s = int(records[1])

		self.dmface2s = []
		for i in range(numface2s):
			dmface2i = self.dmface2()
			parse.property(r, "DMFACE2", 0)

			records = parse.property(r, "PASSABLE", 1)
			dmface2i.passable = int(records[1])
			records = parse.property(r, "TRIANGLE", 3)
			dmface2i.triangle = int(records[1]), int(records[2]), int(records[3])
			self.dmface2s.append(dmface2i)
		records = parse.property(r, "NUMMESHOPS", 1)
		nummeshops = int(records[1])

		self.meshops = []
		for i in range(nummeshops):
			meshopi = self.meshop()
			records = parse.property(r, "MESHOP", 5)
			meshopi.meshop = int(records[1]), int(records[2]), float(records[3]), int(records[4]), int(records[5])
			self.meshops.append(meshopi)
		records = parse.property(r, "FACEMATERIALGROUPS", 3)
		self.facematerialgroups = int(records[1]), int(records[2]), int(records[3])
		records = parse.property(r, "VERTEXMATERIALGROUPS", 3)
		self.vertexmaterialgroups = int(records[1]), int(records[2]), int(records[3])
		records = parse.property(r, "BOUNDINGBOXMIN", 3)
		self.boundingboxmin = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "BOUNDINGBOXMAX", 3)
		self.boundingboxmax = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = parse.property(r, "FPSCALE", 1)
		self.fpscale = int(records[1])
		records = parse.property(r, "HEXONEFLAG", 1)
		self.hexoneflag = int(records[1])
		records = parse.property(r, "HEXTWOFLAG", 1)
		self.hextwoflag = int(records[1])
		records = parse.property(r, "HEXFOURTHOUSANDFLAG", 1)
		self.hexfourthousandflag = int(records[1])
		records = parse.property(r, "HEXEIGHTTHOUSANDFLAG", 1)
		self.hexeightthousandflag = int(records[1])
		records = parse.property(r, "HEXTENTHOUSANDFLAG", 1)
		self.hextenthousandflag = int(records[1])
		records = parse.property(r, "HEXTWENTYTHOUSANDFLAG", 1)
		self.hextwentythousandflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"TAGINDEX \"{self.tagindex}\"\n")
		w.write(f"CENTEROFFSET \"{self.centeroffset}\"\n")
		w.write(f"NUMVERTICES \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMUVS \"{len(self.uvs)}\"\n")
		for uvi in self.uvs:
			w.write(f"UV \"{uvi.uv}\"\n")
		w.write(f"NUMVERTEXNORMALS \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMVERTEXCOLORS \"{len(self.rgbas)}\"\n")
		for rgbai in self.rgbas:
			w.write(f"RGBA \"{rgbai.rgba}\"\n")
		w.write(f"SKINASSIGNMENTGROUPS \"{self.skinassignmentgroups}\"\n")
		w.write(f"MATERIALPALETTE \"{self.materialpalette}\"\n")
		w.write(f"DMTRACKINST \"{self.dmtrackinst}\"\n")
		w.write(f"POLYHEDRON \"{self.polyhedron}\"\n")
		w.write(f"DEFINITION \"{self.definition}\"\n")
		w.write(f"NUMFACE2S \"{len(self.dmface2s)}\"\n")
		for dmface2i in self.dmface2s:
			w.write(f"DMFACE2\n")
			w.write(f"PASSABLE \"{dmface2i.passable}\"\n")
			w.write(f"TRIANGLE \"{dmface2i.triangle}\"\n")
		w.write(f"NUMMESHOPS \"{len(self.meshops)}\"\n")
		for meshopi in self.meshops:
			w.write(f"MESHOP \"{meshopi.meshop}\"\n")
		w.write(f"FACEMATERIALGROUPS \"{self.facematerialgroups}\"\n")
		w.write(f"VERTEXMATERIALGROUPS \"{self.vertexmaterialgroups}\"\n")
		w.write(f"BOUNDINGBOXMIN \"{self.boundingboxmin}\"\n")
		w.write(f"BOUNDINGBOXMAX \"{self.boundingboxmax}\"\n")
		w.write(f"BOUNDINGRADIUS \"{self.boundingradius}\"\n")
		w.write(f"FPSCALE \"{self.fpscale}\"\n")
		w.write(f"HEXONEFLAG \"{self.hexoneflag}\"\n")
		w.write(f"HEXTWOFLAG \"{self.hextwoflag}\"\n")
		w.write(f"HEXFOURTHOUSANDFLAG \"{self.hexfourthousandflag}\"\n")
		w.write(f"HEXEIGHTTHOUSANDFLAG \"{self.hexeightthousandflag}\"\n")
		w.write(f"HEXTENTHOUSANDFLAG \"{self.hextenthousandflag}\"\n")
		w.write(f"HEXTWENTYTHOUSANDFLAG \"{self.hextwentythousandflag}\"\n")

