# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgmodeldef:
	@staticmethod
	def definition():
		return "EQGMODELDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.materials = []
		self.vertices = []
		self.faces = []
		self.bones = []

	class materialtag:
		materialtag:str
		shadertag:str
		hexoneflag:int
		animsleep:int

		def __init__(self):
			self.materialtag = "" #3
			self.shadertag = "" #3
			self.hexoneflag = 0 #3
			self.animsleep = 0 #3
			self.properties = []
			self.animtextures = []

		class property:
			property:tuple[str, int, str]

			def __init__(self):
				self.property = ("", 0, "") #4

		class texture:
			texture:str

			def __init__(self):
				self.texture = "" #4

	class vertex:
		xyz:tuple[float, float, float]
		uv:tuple[float, float]
		uv2:tuple[float, float]
		normal:tuple[float, float, float]
		tint:tuple[int, int, int, int]

		def __init__(self):
			self.xyz = (0.0, 0.0, 0.0) #3
			self.uv = (0.0, 0.0) #3
			self.uv2 = (0.0, 0.0) #3
			self.normal = (0.0, 0.0, 0.0) #3
			self.tint = (0, 0, 0, 0) #3
			self.weights = []

		class weight:
			weight:tuple[int, float]

			def __init__(self):
				self.weight = (0, 0.0) #4

	class face:
		triangle:tuple[int, int, int]
		material:str
		passable:int
		transparent:int
		collisionrequired:int
		culled:int
		degenerate:int

		def __init__(self):
			self.triangle = (0, 0, 0) #3
			self.material = "" #3
			self.passable = 0 #3
			self.transparent = 0 #3
			self.collisionrequired = 0 #3
			self.culled = 0 #3
			self.degenerate = 0 #3

	class bone:
		bone:str
		next:int
		children:int
		childindex:int
		pivot:tuple[float, float, float]
		quaternion:tuple[float, float, float, float]
		scale:tuple[float, float, float]

		def __init__(self):
			self.bone = "" #3
			self.next = 0 #3
			self.children = 0 #3
			self.childindex = 0 #3
			self.pivot = (0.0, 0.0, 0.0) #3
			self.quaternion = (0.0, 0.0, 0.0, 0.0) #3
			self.scale = (0.0, 0.0, 0.0) #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMMATERIALS", 1)
		nummaterials = int(records[1])

		self.materials = []
		for i in range(nummaterials):
			materialtagi = type(self).materialtag()
			records = property(r, "MATERIALTAG", 1)
			materialtagi.materialtag = str(records[1])
			records = property(r, "SHADERTAG", 1)
			materialtagi.shadertag = str(records[1])
			records = property(r, "HEXONEFLAG", 1)
			materialtagi.hexoneflag = int(records[1])
			records = property(r, "NUMPROPERTIES", 1)
			numproperties = int(records[1])

			materialtagi.properties = []
			for j in range(numproperties):
				propertyj = type(materialtagi).property()
				records = property(r, "PROPERTY", 3)
				propertyj.property = (str(records[1]), int(records[2]), str(records[3]))
				materialtagi.properties.append(propertyj)
			records = property(r, "ANIMSLEEP", 1)
			materialtagi.animsleep = int(records[1])
			records = property(r, "NUMANIMTEXTURES", 1)
			numanimtextures = int(records[1])

			materialtagi.animtextures = []
			for j in range(numanimtextures):
				texturej = type(materialtagi).texture()
				records = property(r, "TEXTURE", 1)
				texturej.texture = str(records[1])
				materialtagi.animtextures.append(texturej)
			self.materials.append(materialtagi)
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			vertexi = type(self).vertex()
			property(r, "VERTEX", 0)

			records = property(r, "XYZ", 3)
			vertexi.xyz = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "UV", 2)
			vertexi.uv = (float(records[1]), float(records[2]))
			records = property(r, "UV2", 2)
			vertexi.uv2 = (float(records[1]), float(records[2]))
			records = property(r, "NORMAL", 3)
			vertexi.normal = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "TINT", 4)
			vertexi.tint = (int(records[1]), int(records[2]), int(records[3]), int(records[4]))
			records = property(r, "NUMWEIGHTS", 1)
			numweights = int(records[1])

			vertexi.weights = []
			for j in range(numweights):
				weightj = type(vertexi).weight()
				records = property(r, "WEIGHT", 2)
				weightj.weight = (int(records[1]), float(records[2]))
				vertexi.weights.append(weightj)
			self.vertices.append(vertexi)
		records = property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.faces = []
		for i in range(numfaces):
			facei = type(self).face()
			property(r, "FACE", 0)

			records = property(r, "TRIANGLE", 3)
			facei.triangle = (int(records[1]), int(records[2]), int(records[3]))
			records = property(r, "MATERIAL", 1)
			facei.material = str(records[1])
			records = property(r, "PASSABLE", 1)
			facei.passable = int(records[1])
			records = property(r, "TRANSPARENT", 1)
			facei.transparent = int(records[1])
			records = property(r, "COLLISIONREQUIRED", 1)
			facei.collisionrequired = int(records[1])
			records = property(r, "CULLED", 1)
			facei.culled = int(records[1])
			records = property(r, "DEGENERATE", 1)
			facei.degenerate = int(records[1])
			self.faces.append(facei)
		records = property(r, "NUMBONES", 1)
		numbones = int(records[1])

		self.bones = []
		for i in range(numbones):
			bonei = type(self).bone()
			records = property(r, "BONE", 1)
			bonei.bone = str(records[1])
			records = property(r, "NEXT", 1)
			bonei.next = int(records[1])
			records = property(r, "CHILDREN", 1)
			bonei.children = int(records[1])
			records = property(r, "CHILDINDEX", 1)
			bonei.childindex = int(records[1])
			records = property(r, "PIVOT", 3)
			bonei.pivot = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "QUATERNION", 4)
			bonei.quaternion = (float(records[1]), float(records[2]), float(records[3]), float(records[4]))
			records = property(r, "SCALE", 3)
			bonei.scale = (float(records[1]), float(records[2]), float(records[3]))
			self.bones.append(bonei)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMMATERIALS {len(self.materials)}\n")
		for materialtagi in self.materials:
			w.write(f"\t\tMATERIALTAG \"{materialtagi.materialtag}\"\n")
			w.write(f"\t\tSHADERTAG \"{materialtagi.shadertag}\"\n")
			w.write(f"\t\tHEXONEFLAG {materialtagi.hexoneflag}\n")
			w.write(f"\t\tNUMPROPERTIES {len(materialtagi.properties)}\n")
			for propertyj in materialtagi.properties:
				w.write(f"\t\t\tPROPERTY {propertyj.property[0]} {propertyj.property[1]} {propertyj.property[2]}\n")
			w.write(f"\t\tANIMSLEEP {materialtagi.animsleep}\n")
			w.write(f"\t\tNUMANIMTEXTURES {len(materialtagi.animtextures)}\n")
			for texturej in materialtagi.animtextures:
				w.write(f"\t\t\tTEXTURE \"{texturej.texture}\"\n")
		w.write(f"\tNUMVERTICES {len(self.vertices)}\n")
		for vertexi in self.vertices:
			w.write(f"\t\tVERTEX\n")
			w.write(f"\t\tXYZ {format(vertexi.xyz[0], '.8e')} {format(vertexi.xyz[1], '.8e')} {format(vertexi.xyz[2], '.8e')}\n")
			w.write(f"\t\tUV {format(vertexi.uv[0], '.8e')} {format(vertexi.uv[1], '.8e')}\n")
			w.write(f"\t\tUV2 {format(vertexi.uv2[0], '.8e')} {format(vertexi.uv2[1], '.8e')}\n")
			w.write(f"\t\tNORMAL {format(vertexi.normal[0], '.8e')} {format(vertexi.normal[1], '.8e')} {format(vertexi.normal[2], '.8e')}\n")
			w.write(f"\t\tTINT {vertexi.tint[0]} {vertexi.tint[1]} {vertexi.tint[2]} {vertexi.tint[3]}\n")
			w.write(f"\t\tNUMWEIGHTS {len(vertexi.weights)}\n")
			for weightj in vertexi.weights:
				w.write(f"\t\t\tWEIGHT {weightj.weight[0]} {format(weightj.weight[1], '.8e')}\n")
		w.write(f"\tNUMFACES {len(self.faces)}\n")
		for facei in self.faces:
			w.write(f"\t\tFACE\n")
			w.write(f"\t\tTRIANGLE {facei.triangle[0]} {facei.triangle[1]} {facei.triangle[2]}\n")
			w.write(f"\t\tMATERIAL \"{facei.material}\"\n")
			w.write(f"\t\tPASSABLE {facei.passable}\n")
			w.write(f"\t\tTRANSPARENT {facei.transparent}\n")
			w.write(f"\t\tCOLLISIONREQUIRED {facei.collisionrequired}\n")
			w.write(f"\t\tCULLED {facei.culled}\n")
			w.write(f"\t\tDEGENERATE {facei.degenerate}\n")
		w.write(f"\tNUMBONES {len(self.bones)}\n")
		for bonei in self.bones:
			w.write(f"\t\tBONE \"{bonei.bone}\"\n")
			w.write(f"\t\tNEXT {bonei.next}\n")
			w.write(f"\t\tCHILDREN {bonei.children}\n")
			w.write(f"\t\tCHILDINDEX {bonei.childindex}\n")
			w.write(f"\t\tPIVOT {format(bonei.pivot[0], '.8e')} {format(bonei.pivot[1], '.8e')} {format(bonei.pivot[2], '.8e')}\n")
			w.write(f"\t\tQUATERNION {format(bonei.quaternion[0], '.8e')} {format(bonei.quaternion[1], '.8e')} {format(bonei.quaternion[2], '.8e')} {format(bonei.quaternion[3], '.8e')}\n")
			w.write(f"\t\tSCALE {format(bonei.scale[0], '.8e')} {format(bonei.scale[1], '.8e')} {format(bonei.scale[2], '.8e')}\n")
		return ""

