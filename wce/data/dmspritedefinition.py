# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class dmspritedefinition:
	@staticmethod
	def definition():
		return "DMSPRITEDEFINITION"

	tag:str
	tagindex:int # The index of the tag
	fragment1:int # Fragment 1
	materialpalette:str # Material palette tag
	fragment3:int # Fragment 3
	center:tuple[tuple[float, None], tuple[float, None], tuple[float, None]] # center?
	params1:tuple[tuple[int, None], tuple[int, None], tuple[int, None]] # params1

	class xyz:
		xyz:tuple[float, float, float] # The coordinates of a vertex

	xyzs:list[xyz]

	class uv:
		uv:tuple[float, float] # The coordinates of a texture normal

	uvs:list[uv]

	class xyz:
		xyz:tuple[float, float, float] # The coordinates of a texture normal

	xyzs:list[xyz]

	class rgba:
		rgba:tuple[int, int, int, int] # The coordinates of a vertex

	rgbas:list[rgba]

	class dmface:

		flag:int # face flags

		data:tuple[int, int, int, int] # face data

		triangle:tuple[int, int, int] # Triangle indexes

	dmfaces:list[dmface]

	class meshop:
		meshop:tuple[int, int, float, int, int] # A mesh operation

	meshops:list[meshop]
	skinassignmentgroups:tuple[list[str]] # The skin assignment groups
	data8:int # data 8 information
	facematerialgroups:tuple[int, int, int] # The face material groups
	vertexmaterialgroups:tuple[int, int, int] # The vertex material groups
	params2:tuple[tuple[int, None], tuple[int, None], tuple[int, None]] # params2

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "FRAGMENT1", 1)
		self.fragment1 = int(records[1])
		records = parse.property(r, "MATERIALPALETTE", 1)
		self.materialpalette = str(records[1])
		records = parse.property(r, "FRAGMENT3", 1)
		self.fragment3 = int(records[1])
		records = parse.property(r, "CENTER?", 3)
		self.center = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "PARAMS1?", 3)
		self.params1 = (int(records[1]) if records[1] != "NULL" else None), (int(records[2]) if records[2] != "NULL" else None), (int(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.xyzs = []
		for i in range(numvertices):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMTEXCOORDS", 1)
		numtexcoords = int(records[1])

		self.uvs = []
		for i in range(numtexcoords):
			uvi = self.uv()
			records = parse.property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.uvs.append(uvi)
		records = parse.property(r, "NUMNORMALS", 1)
		numnormals = int(records[1])

		self.xyzs = []
		for i in range(numnormals):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMCOLORS", 1)
		numcolors = int(records[1])

		self.rgbas = []
		for i in range(numcolors):
			rgbai = self.rgba()
			records = parse.property(r, "RGBA", 4)
			rgbai.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			self.rgbas.append(rgbai)
		records = parse.property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.dmfaces = []
		for i in range(numfaces):
			dmfacei = self.dmface()
			parse.property(r, "DMFACE", 0)

			records = parse.property(r, "FLAG", 1)
			dmfacei.flag = int(records[1])
			records = parse.property(r, "DATA", 4)
			dmfacei.data = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			records = parse.property(r, "TRIANGLE", 3)
			dmfacei.triangle = int(records[1]), int(records[2]), int(records[3])
			self.dmfaces.append(dmfacei)
		records = parse.property(r, "NUMMESHOPS", 1)
		nummeshops = int(records[1])

		self.meshops = []
		for i in range(nummeshops):
			meshopi = self.meshop()
			records = parse.property(r, "MESHOP", 5)
			meshopi.meshop = int(records[1]), int(records[2]), float(records[3]), int(records[4]), int(records[5])
			self.meshops.append(meshopi)
		records = parse.property(r, "SKINASSIGNMENTGROUPS", -1)
		self.skinassignmentgroups = records[1:]

		records = parse.property(r, "DATA8", 1)
		self.data8 = int(records[1])
		records = parse.property(r, "FACEMATERIALGROUPS", 3)
		self.facematerialgroups = int(records[1]), int(records[2]), int(records[3])
		records = parse.property(r, "VERTEXMATERIALGROUPS", 3)
		self.vertexmaterialgroups = int(records[1]), int(records[2]), int(records[3])
		records = parse.property(r, "PARAMS2?", 3)
		self.params2 = (int(records[1]) if records[1] != "NULL" else None), (int(records[2]) if records[2] != "NULL" else None), (int(records[3]) if records[3] != "NULL" else None)

	def write(self, w:io.TextIOWrapper):
		w.write(f"TAGINDEX \"{self.tagindex}\"\n")
		w.write(f"FRAGMENT1 \"{self.fragment1}\"\n")
		w.write(f"MATERIALPALETTE \"{self.materialpalette}\"\n")
		w.write(f"FRAGMENT3 \"{self.fragment3}\"\n")
		w.write(f"CENTER? \"{self.center}\"\n")
		w.write(f"PARAMS1? \"{self.params1}\"\n")
		w.write(f"NUMVERTICES \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMTEXCOORDS \"{len(self.uvs)}\"\n")
		for uvi in self.uvs:
			w.write(f"UV \"{uvi.uv}\"\n")
		w.write(f"NUMNORMALS \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMCOLORS \"{len(self.rgbas)}\"\n")
		for rgbai in self.rgbas:
			w.write(f"RGBA \"{rgbai.rgba}\"\n")
		w.write(f"NUMFACES \"{len(self.dmfaces)}\"\n")
		for dmfacei in self.dmfaces:
			w.write(f"DMFACE\n")
			w.write(f"FLAG \"{dmfacei.flag}\"\n")
			w.write(f"DATA \"{dmfacei.data}\"\n")
			w.write(f"TRIANGLE \"{dmfacei.triangle}\"\n")
		w.write(f"NUMMESHOPS \"{len(self.meshops)}\"\n")
		for meshopi in self.meshops:
			w.write(f"MESHOP \"{meshopi.meshop}\"\n")
		w.write(f"SKINASSIGNMENTGROUPS \"{self.skinassignmentgroups}\"\n")
		w.write(f"DATA8 \"{self.data8}\"\n")
		w.write(f"FACEMATERIALGROUPS \"{self.facematerialgroups}\"\n")
		w.write(f"VERTEXMATERIALGROUPS \"{self.vertexmaterialgroups}\"\n")
		w.write(f"PARAMS2? \"{self.params2}\"\n")

