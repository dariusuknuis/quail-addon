# Generated from quail, DO NOT EDIT
import io
from .parse import property

class dmspritedef2:
	@staticmethod
	def definition():
		return "DMSPRITEDEF2"

	tag:str
	tagindex:int # The index of the tag
	centeroffset:tuple[float, float, float] # The center offset of the sprite

	class vxyz:
		vxyz:tuple[float, float, float] # The coordinates of a vertex

	vxyzs:list[vxyz]

	class uv:
		uv:tuple[float, float] # UV entry

	uvs:list[uv]

	class nxyz:
		nxyz:tuple[float, float, float] # The coordinates of a texture normal

	nxyzs:list[nxyz]

	class rgba:
		rgba:tuple[int, int, int, int] # The coordinates of a vertex

	rgbas:list[rgba]
	skinassignmentgroups:tuple[list[str]] # The skin assignment groups
	materialpalette:str # The material palette used by the sprite
	dmtrackinst:str # The DM track instance
	sprite:str # The definition reference

	class dmface2:

		passable:int # Is face passable?

		triangle:tuple[int, int, int] # Triangle indexes

	dmface2s:list[dmface2]

	class meshop:
		meshop:tuple[int, int, float, int, int] # A mesh operation

	meshops:list[meshop]
	facematerialgroups:list[str] # The face material groups
	vertexmaterialgroups:list[str] # The vertex material groups
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
		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "CENTEROFFSET", 3)
		self.centeroffset = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vxyzs = []
		for i in range(numvertices):
			vxyzi = self.vxyz()
			records = property(r, "VXYZ", 3)
			vxyzi.vxyz = float(records[1]), float(records[2]), float(records[3])
			self.vxyzs.append(vxyzi)
		records = property(r, "NUMUVS", 1)
		numuvs = int(records[1])

		self.uvs = []
		for i in range(numuvs):
			uvi = self.uv()
			records = property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.uvs.append(uvi)
		records = property(r, "NUMVERTEXNORMALS", 1)
		numvertexnormals = int(records[1])

		self.nxyzs = []
		for i in range(numvertexnormals):
			nxyzi = self.nxyz()
			records = property(r, "NXYZ", 3)
			nxyzi.nxyz = float(records[1]), float(records[2]), float(records[3])
			self.nxyzs.append(nxyzi)
		records = property(r, "NUMVERTEXCOLORS", 1)
		numvertexcolors = int(records[1])

		self.rgbas = []
		for i in range(numvertexcolors):
			rgbai = self.rgba()
			records = property(r, "RGBA", 4)
			rgbai.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			self.rgbas.append(rgbai)
		records = property(r, "SKINASSIGNMENTGROUPS", -1)
		self.skinassignmentgroups = records[1:]

		records = property(r, "MATERIALPALETTE", 1)
		self.materialpalette = str(records[1])
		records = property(r, "DMTRACKINST", 1)
		self.dmtrackinst = str(records[1])
		property(r, "POLYHEDRON", 0)

		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "NUMFACE2S", 1)
		numface2s = int(records[1])

		self.dmface2s = []
		for i in range(numface2s):
			dmface2i = self.dmface2()
			property(r, "DMFACE2", 0)

			records = property(r, "PASSABLE", 1)
			dmface2i.passable = int(records[1])
			records = property(r, "TRIANGLE", 3)
			dmface2i.triangle = int(records[1]), int(records[2]), int(records[3])
			self.dmface2s.append(dmface2i)
		records = property(r, "NUMMESHOPS", 1)
		nummeshops = int(records[1])

		self.meshops = []
		for i in range(nummeshops):
			meshopi = self.meshop()
			records = property(r, "MESHOP", 5)
			meshopi.meshop = int(records[1]), int(records[2]), float(records[3]), int(records[4]), int(records[5])
			self.meshops.append(meshopi)
		records = property(r, "FACEMATERIALGROUPS", -1)
		self.facematerialgroups = records[1:]

		records = property(r, "VERTEXMATERIALGROUPS", -1)
		self.vertexmaterialgroups = records[1:]

		records = property(r, "BOUNDINGBOXMIN", 3)
		self.boundingboxmin = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "BOUNDINGBOXMAX", 3)
		self.boundingboxmax = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = property(r, "FPSCALE", 1)
		self.fpscale = int(records[1])
		records = property(r, "HEXONEFLAG", 1)
		self.hexoneflag = int(records[1])
		records = property(r, "HEXTWOFLAG", 1)
		self.hextwoflag = int(records[1])
		records = property(r, "HEXFOURTHOUSANDFLAG", 1)
		self.hexfourthousandflag = int(records[1])
		records = property(r, "HEXEIGHTTHOUSANDFLAG", 1)
		self.hexeightthousandflag = int(records[1])
		records = property(r, "HEXTENTHOUSANDFLAG", 1)
		self.hextenthousandflag = int(records[1])
		records = property(r, "HEXTWENTYTHOUSANDFLAG", 1)
		self.hextwentythousandflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tCENTEROFFSET \"{self.centeroffset}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.vxyzs)}\"\n")
		for vxyzi in self.vxyzs:
			w.write(f"\t\tVXYZ \"{vxyzi.vxyz}\"\n")
		w.write(f"\tNUMUVS \"{len(self.uvs)}\"\n")
		for uvi in self.uvs:
			w.write(f"\t\tUV \"{uvi.uv}\"\n")
		w.write(f"\tNUMVERTEXNORMALS \"{len(self.nxyzs)}\"\n")
		for nxyzi in self.nxyzs:
			w.write(f"\t\tNXYZ \"{nxyzi.nxyz}\"\n")
		w.write(f"\tNUMVERTEXCOLORS \"{len(self.rgbas)}\"\n")
		for rgbai in self.rgbas:
			w.write(f"\t\tRGBA \"{rgbai.rgba}\"\n")
		w.write(f"SKINASSIGNMENTGROUPS \"{self.skinassignmentgroups}\"\n")
		w.write(f"\tMATERIALPALETTE \"{self.materialpalette}\"\n")
		w.write(f"\tDMTRACKINST \"{self.dmtrackinst}\"\n")
		w.write(f"\tPOLYHEDRON\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tNUMFACE2S \"{len(self.dmface2s)}\"\n")
		for dmface2i in self.dmface2s:
			w.write(f"\t\tDMFACE2\n")
			w.write(f"\t\tPASSABLE \"{dmface2i.passable}\"\n")
			w.write(f"\t\tTRIANGLE \"{dmface2i.triangle}\"\n")
		w.write(f"\tNUMMESHOPS \"{len(self.meshops)}\"\n")
		for meshopi in self.meshops:
			w.write(f"\t\tMESHOP \"{meshopi.meshop}\"\n")
		w.write(f"FACEMATERIALGROUPS \"{self.facematerialgroups}\"\n")
		w.write(f"VERTEXMATERIALGROUPS \"{self.vertexmaterialgroups}\"\n")
		w.write(f"\tBOUNDINGBOXMIN \"{self.boundingboxmin}\"\n")
		w.write(f"\tBOUNDINGBOXMAX \"{self.boundingboxmax}\"\n")
		w.write(f"\tBOUNDINGRADIUS \"{self.boundingradius}\"\n")
		w.write(f"\tFPSCALE \"{self.fpscale}\"\n")
		w.write(f"\tHEXONEFLAG \"{self.hexoneflag}\"\n")
		w.write(f"\tHEXTWOFLAG \"{self.hextwoflag}\"\n")
		w.write(f"\tHEXFOURTHOUSANDFLAG \"{self.hexfourthousandflag}\"\n")
		w.write(f"\tHEXEIGHTTHOUSANDFLAG \"{self.hexeightthousandflag}\"\n")
		w.write(f"\tHEXTENTHOUSANDFLAG \"{self.hextenthousandflag}\"\n")
		w.write(f"\tHEXTWENTYTHOUSANDFLAG \"{self.hextwentythousandflag}\"\n")

