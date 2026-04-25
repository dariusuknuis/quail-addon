# Generated from quail, DO NOT EDIT
import io
from .parse import property

class dmspritedef2:
	@staticmethod
	def definition():
		return "DMSPRITEDEF2"

	tag:str
	centeroffset:tuple[float, float, float]
	skinassignmentgroups:list[str]
	materialpalette:str
	dmtrackinst:str
	dmrgbtrack:str
	sprite:str
	facematerialgroups:list[str]
	vertexmaterialgroups:list[str]
	params2:tuple[float, float, float]
	boundingboxmin:tuple[float, float, float]
	boundingboxmax:tuple[float, float, float]
	boundingradius:float
	fpscale:int
	usecenteroffset:int
	useboundingradius:int
	useparams2:int
	useboundingbox:int
	usevertexcoloralpha:int
	spritedefpolyhedron:int

	def __init__(self):
		self.tag = ""
		self.centeroffset = (0.0, 0.0, 0.0) #2
		self.skinassignmentgroups = [] #2
		self.materialpalette = "" #2
		self.dmtrackinst = "" #2
		self.dmrgbtrack = "" #2
		self.sprite = "" #2
		self.facematerialgroups = [] #2
		self.vertexmaterialgroups = [] #2
		self.params2 = (0.0, 0.0, 0.0) #2
		self.boundingboxmin = (0.0, 0.0, 0.0) #2
		self.boundingboxmax = (0.0, 0.0, 0.0) #2
		self.boundingradius = 0.0 #2
		self.fpscale = 0 #2
		self.usecenteroffset = 0 #2
		self.useboundingradius = 0 #2
		self.useparams2 = 0 #2
		self.useboundingbox = 0 #2
		self.usevertexcoloralpha = 0 #2
		self.spritedefpolyhedron = 0 #2
		self.vertices = []
		self.uvs = []
		self.vertexnormals = []
		self.vertexcolors = []
		self.face2s = []
		self.meshops = []

	class vxyz:
		vxyz:tuple[float, float, float]

		def __init__(self):
			self.vxyz = (0.0, 0.0, 0.0) #3

	class uv:
		uv:tuple[float, float]

		def __init__(self):
			self.uv = (0.0, 0.0) #3

	class nxyz:
		nxyz:tuple[float, float, float]

		def __init__(self):
			self.nxyz = (0.0, 0.0, 0.0) #3

	class rgba:
		rgba:tuple[int, int, int, int]

		def __init__(self):
			self.rgba = (0, 0, 0, 0) #3

	class dmface2:
		passable:int
		triangle:tuple[int, int, int]

		def __init__(self):
			self.passable = 0 #3
			self.triangle = (0, 0, 0) #3

	class meshop:
		meshop:tuple[int, int, float, int, int]

		def __init__(self):
			self.meshop = (0, 0, 0.0, 0, 0) #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "CENTEROFFSET", 3)
		self.centeroffset = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			vxyzi = type(self).vxyz()
			records = property(r, "VXYZ", 3)
			vxyzi.vxyz = (float(records[1]), float(records[2]), float(records[3]))
			self.vertices.append(vxyzi)
		records = property(r, "NUMUVS", 1)
		numuvs = int(records[1])

		self.uvs = []
		for i in range(numuvs):
			uvi = type(self).uv()
			records = property(r, "UV", 2)
			uvi.uv = (float(records[1]), float(records[2]))
			self.uvs.append(uvi)
		records = property(r, "NUMVERTEXNORMALS", 1)
		numvertexnormals = int(records[1])

		self.vertexnormals = []
		for i in range(numvertexnormals):
			nxyzi = type(self).nxyz()
			records = property(r, "NXYZ", 3)
			nxyzi.nxyz = (float(records[1]), float(records[2]), float(records[3]))
			self.vertexnormals.append(nxyzi)
		records = property(r, "NUMVERTEXCOLORS", 1)
		numvertexcolors = int(records[1])

		self.vertexcolors = []
		for i in range(numvertexcolors):
			rgbai = type(self).rgba()
			records = property(r, "RGBA", 4)
			rgbai.rgba = (int(records[1]), int(records[2]), int(records[3]), int(records[4]))
			self.vertexcolors.append(rgbai)
		records = property(r, "SKINASSIGNMENTGROUPS", -1)
		self.skinassignmentgroups = records[1:]

		records = property(r, "MATERIALPALETTE", 1)
		self.materialpalette = str(records[1])
		records = property(r, "DMTRACKINST", 1)
		self.dmtrackinst = str(records[1])
		records = property(r, "DMRGBTRACK", 1)
		self.dmrgbtrack = str(records[1])
		property(r, "POLYHEDRON", 0)

		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "NUMFACE2S", 1)
		numface2s = int(records[1])

		self.face2s = []
		for i in range(numface2s):
			dmface2i = type(self).dmface2()
			property(r, "DMFACE2", 0)

			records = property(r, "PASSABLE", 1)
			dmface2i.passable = int(records[1])
			records = property(r, "TRIANGLE", 3)
			dmface2i.triangle = (int(records[1]), int(records[2]), int(records[3]))
			self.face2s.append(dmface2i)
		records = property(r, "NUMMESHOPS", 1)
		nummeshops = int(records[1])

		self.meshops = []
		for i in range(nummeshops):
			meshopi = type(self).meshop()
			records = property(r, "MESHOP", 5)
			meshopi.meshop = (int(records[1]), int(records[2]), float(records[3]), int(records[4]), int(records[5]))
			self.meshops.append(meshopi)
		records = property(r, "FACEMATERIALGROUPS", -1)
		self.facematerialgroups = records[1:]

		records = property(r, "VERTEXMATERIALGROUPS", -1)
		self.vertexmaterialgroups = records[1:]

		records = property(r, "PARAMS2", 3)
		self.params2 = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BOUNDINGBOXMIN", 3)
		self.boundingboxmin = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BOUNDINGBOXMAX", 3)
		self.boundingboxmax = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BOUNDINGRADIUS", 1)
		self.boundingradius = float(records[1])
		records = property(r, "FPSCALE", 1)
		self.fpscale = int(records[1])
		records = property(r, "USECENTEROFFSET", 1)
		self.usecenteroffset = int(records[1])
		records = property(r, "USEBOUNDINGRADIUS", 1)
		self.useboundingradius = int(records[1])
		records = property(r, "USEPARAMS2", 1)
		self.useparams2 = int(records[1])
		records = property(r, "USEBOUNDINGBOX", 1)
		self.useboundingbox = int(records[1])
		records = property(r, "USEVERTEXCOLORALPHA", 1)
		self.usevertexcoloralpha = int(records[1])
		records = property(r, "SPRITEDEFPOLYHEDRON", 1)
		self.spritedefpolyhedron = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tCENTEROFFSET {format(self.centeroffset[0], '.8e')} {format(self.centeroffset[1], '.8e')} {format(self.centeroffset[2], '.8e')}\n")
		w.write(f"\tNUMVERTICES {len(self.vertices)}\n")
		for vxyzi in self.vertices:
			w.write(f"\t\tVXYZ {format(vxyzi.vxyz[0], '.8e')} {format(vxyzi.vxyz[1], '.8e')} {format(vxyzi.vxyz[2], '.8e')}\n")
		w.write(f"\tNUMUVS {len(self.uvs)}\n")
		for uvi in self.uvs:
			w.write(f"\t\tUV {format(uvi.uv[0], '.8e')} {format(uvi.uv[1], '.8e')}\n")
		w.write(f"\tNUMVERTEXNORMALS {len(self.vertexnormals)}\n")
		for nxyzi in self.vertexnormals:
			w.write(f"\t\tNXYZ {format(nxyzi.nxyz[0], '.8e')} {format(nxyzi.nxyz[1], '.8e')} {format(nxyzi.nxyz[2], '.8e')}\n")
		w.write(f"\tNUMVERTEXCOLORS {len(self.vertexcolors)}\n")
		for rgbai in self.vertexcolors:
			w.write(f"\t\tRGBA {rgbai.rgba[0]} {rgbai.rgba[1]} {rgbai.rgba[2]} {rgbai.rgba[3]}\n")
		w.write(f"\tSKINASSIGNMENTGROUPS {self.skinassignmentgroups[0]} {self.skinassignmentgroups[1]}\n")
		w.write(f"\tMATERIALPALETTE \"{self.materialpalette}\"\n")
		w.write(f"\tDMTRACKINST \"{self.dmtrackinst}\"\n")
		w.write(f"\tDMRGBTRACK \"{self.dmrgbtrack}\"\n")
		w.write(f"\tPOLYHEDRON\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tNUMFACE2S {len(self.face2s)}\n")
		for dmface2i in self.face2s:
			w.write(f"\t\tDMFACE2\n")
			w.write(f"\t\tPASSABLE {dmface2i.passable}\n")
			w.write(f"\t\tTRIANGLE {dmface2i.triangle[0]} {dmface2i.triangle[1]} {dmface2i.triangle[2]}\n")
		w.write(f"\tNUMMESHOPS {len(self.meshops)}\n")
		for meshopi in self.meshops:
			w.write(f"\t\tMESHOP {meshopi.meshop[0]} {meshopi.meshop[1]} {format(meshopi.meshop[2], '.8e')} {meshopi.meshop[3]} {meshopi.meshop[4]}\n")
		w.write(f"\tFACEMATERIALGROUPS {self.facematerialgroups}\n")
		w.write(f"\tVERTEXMATERIALGROUPS {self.vertexmaterialgroups}\n")
		w.write(f"\tPARAMS2 {format(self.params2[0], '.8e')} {format(self.params2[1], '.8e')} {format(self.params2[2], '.8e')}\n")
		w.write(f"\tBOUNDINGBOXMIN {format(self.boundingboxmin[0], '.8e')} {format(self.boundingboxmin[1], '.8e')} {format(self.boundingboxmin[2], '.8e')}\n")
		w.write(f"\tBOUNDINGBOXMAX {format(self.boundingboxmax[0], '.8e')} {format(self.boundingboxmax[1], '.8e')} {format(self.boundingboxmax[2], '.8e')}\n")
		w.write(f"\tBOUNDINGRADIUS {format(self.boundingradius, '.8e')}\n")
		w.write(f"\tFPSCALE {self.fpscale}\n")
		w.write(f"\tUSECENTEROFFSET {self.usecenteroffset}\n")
		w.write(f"\tUSEBOUNDINGRADIUS {self.useboundingradius}\n")
		w.write(f"\tUSEPARAMS2 {self.useparams2}\n")
		w.write(f"\tUSEBOUNDINGBOX {self.useboundingbox}\n")
		w.write(f"\tUSEVERTEXCOLORALPHA {self.usevertexcoloralpha}\n")
		w.write(f"\tSPRITEDEFPOLYHEDRON {self.spritedefpolyhedron}\n")
		return ""

