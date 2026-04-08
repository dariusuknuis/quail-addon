# Generated from quail, DO NOT EDIT
import io
from .parse import property

class dmspritedefinition:
	@staticmethod
	def definition():
		return "DMSPRITEDEFINITION"

	tag:str
	fragment1:int
	materialpalette:str
	fragment3:int
	center:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	params1:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	skinassignmentgroups:list[str]
	data8:int
	facematerialgroups:list[str]
	vertexmaterialgroups:list[str]
	params2:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]

	def __init__(self):
		self.tag = ""
		self.fragment1 = 0 #2
		self.materialpalette = "" #2
		self.fragment3 = 0 #2
		self.center = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.params1 = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.skinassignmentgroups = list[str] #2
		self.data8 = 0 #2
		self.facematerialgroups = list[str] #2
		self.vertexmaterialgroups = list[str] #2
		self.params2 = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.vertices = []
		self.texcoords = []
		self.normals = []
		self.colors = []
		self.faces = []
		self.meshops = []

	class vxyz:
		vxyz:tuple[float, float, float]

		def __init__(self):
			self.vxyz = tuple[float, float, float] #3

	class uv:
		uv:tuple[float, float]

		def __init__(self):
			self.uv = tuple[float, float] #3

	class nxyz:
		nxyz:tuple[float, float, float]

		def __init__(self):
			self.nxyz = tuple[float, float, float] #3

	class rgba:
		rgba:tuple[int, int, int, int]

		def __init__(self):
			self.rgba = tuple[int, int, int, int] #3

	class dmface:
		flag:int
		data:tuple[int, int, int, int]
		triangle:tuple[int, int, int]

		def __init__(self):
			self.flag = 0 #3
			self.data = tuple[int, int, int, int] #3
			self.triangle = tuple[int, int, int] #3

	class meshop:
		meshop:tuple[int, int, float, int, int]

		def __init__(self):
			self.meshop = tuple[int, int, float, int, int] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "FRAGMENT1", 1)
		self.fragment1 = int(records[1])
		records = property(r, "MATERIALPALETTE", 1)
		self.materialpalette = str(records[1])
		records = property(r, "FRAGMENT3", 1)
		self.fragment3 = int(records[1])
		records = property(r, "CENTER?", 3)
		self.center = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "PARAMS1?", 3)
		self.params1 = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			vxyzi = type(self).vxyz()
			records = property(r, "VXYZ", 3)
			vxyzi.vxyz = float(records[1]), float(records[2]), float(records[3])
			self.vertices.append(vxyzi)
		records = property(r, "NUMTEXCOORDS", 1)
		numtexcoords = int(records[1])

		self.texcoords = []
		for i in range(numtexcoords):
			uvi = type(self).uv()
			records = property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.texcoords.append(uvi)
		records = property(r, "NUMNORMALS", 1)
		numnormals = int(records[1])

		self.normals = []
		for i in range(numnormals):
			nxyzi = type(self).nxyz()
			records = property(r, "NXYZ", 3)
			nxyzi.nxyz = float(records[1]), float(records[2]), float(records[3])
			self.normals.append(nxyzi)
		records = property(r, "NUMCOLORS", 1)
		numcolors = int(records[1])

		self.colors = []
		for i in range(numcolors):
			rgbai = type(self).rgba()
			records = property(r, "RGBA", 4)
			rgbai.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			self.colors.append(rgbai)
		records = property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.faces = []
		for i in range(numfaces):
			dmfacei = type(self).dmface()
			property(r, "DMFACE", 0)

			records = property(r, "FLAG", 1)
			dmfacei.flag = int(records[1])
			records = property(r, "DATA", 4)
			dmfacei.data = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			records = property(r, "TRIANGLE", 3)
			dmfacei.triangle = int(records[1]), int(records[2]), int(records[3])
			self.faces.append(dmfacei)
		records = property(r, "NUMMESHOPS", 1)
		nummeshops = int(records[1])

		self.meshops = []
		for i in range(nummeshops):
			meshopi = type(self).meshop()
			records = property(r, "MESHOP", 5)
			meshopi.meshop = int(records[1]), int(records[2]), float(records[3]), int(records[4]), int(records[5])
			self.meshops.append(meshopi)
		records = property(r, "SKINASSIGNMENTGROUPS", -1)
		self.skinassignmentgroups = records[1:]

		records = property(r, "DATA8", 1)
		self.data8 = int(records[1])
		records = property(r, "FACEMATERIALGROUPS", -1)
		self.facematerialgroups = records[1:]

		records = property(r, "VERTEXMATERIALGROUPS", -1)
		self.vertexmaterialgroups = records[1:]

		records = property(r, "PARAMS2?", 3)
		self.params2 = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tFRAGMENT1 \"{self.fragment1}\"\n")
		w.write(f"\tMATERIALPALETTE \"{self.materialpalette}\"\n")
		w.write(f"\tFRAGMENT3 \"{self.fragment3}\"\n")
		w.write(f"\tCENTER? \"{self.center}\"\n")
		w.write(f"\tPARAMS1? \"{self.params1}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.vertices)}\"\n")
		for vxyzi in self.vertices:
			w.write(f"\t\tVXYZ \"{vxyzi.vxyz}\"\n")
		w.write(f"\tNUMTEXCOORDS \"{len(self.texcoords)}\"\n")
		for uvi in self.texcoords:
			w.write(f"\t\tUV \"{uvi.uv}\"\n")
		w.write(f"\tNUMNORMALS \"{len(self.normals)}\"\n")
		for nxyzi in self.normals:
			w.write(f"\t\tNXYZ \"{nxyzi.nxyz}\"\n")
		w.write(f"\tNUMCOLORS \"{len(self.colors)}\"\n")
		for rgbai in self.colors:
			w.write(f"\t\tRGBA \"{rgbai.rgba}\"\n")
		w.write(f"\tNUMFACES \"{len(self.faces)}\"\n")
		for dmfacei in self.faces:
			w.write(f"\t\tDMFACE\n")
			w.write(f"\t\tFLAG \"{dmfacei.flag}\"\n")
			w.write(f"\t\tDATA \"{dmfacei.data}\"\n")
			w.write(f"\t\tTRIANGLE \"{dmfacei.triangle}\"\n")
		w.write(f"\tNUMMESHOPS \"{len(self.meshops)}\"\n")
		for meshopi in self.meshops:
			w.write(f"\t\tMESHOP \"{meshopi.meshop}\"\n")
		w.write(f"\tSKINASSIGNMENTGROUPS \"{self.skinassignmentgroups}\"\n")
		w.write(f"\tDATA8 \"{self.data8}\"\n")
		w.write(f"\tFACEMATERIALGROUPS \"{self.facematerialgroups}\"\n")
		w.write(f"\tVERTEXMATERIALGROUPS \"{self.vertexmaterialgroups}\"\n")
		w.write(f"\tPARAMS2? \"{self.params2}\"\n")
		return ""

