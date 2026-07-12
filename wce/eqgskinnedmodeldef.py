# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgskinnedmodeldef:
	@staticmethod
	def definition():
		return "EQGSKINNEDMODELDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.materials = []
		self.bones = []
		self.models = []

	class materialtag:
		materialtag:str
		shadertag:str
		animsleep:int

		def __init__(self):
			self.materialtag = "" #3
			self.shadertag = "" #3
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

	class model:
		model:str
		mainpiece:int

		def __init__(self):
			self.model = "" #3
			self.mainpiece = 0 #3
			self.vertices = []
			self.faces = []

		class vertex:
			xyz:tuple[float, float, float]
			uv:tuple[float, float]
			uv2:tuple[float, float]
			normal:tuple[float, float, float]
			tint:tuple[int, int, int, int]

			def __init__(self):
				self.xyz = (0.0, 0.0, 0.0) #4
				self.uv = (0.0, 0.0) #4
				self.uv2 = (0.0, 0.0) #4
				self.normal = (0.0, 0.0, 0.0) #4
				self.tint = (0, 0, 0, 0) #4
				self.weights = []

			class weight:
				weight:tuple[int, float]

				def __init__(self):
					self.weight = (0, 0.0) #5

		class face:
			triangle:tuple[int, int, int]
			material:str
			passable:int
			transparent:int
			collisionrequired:int
			culled:int
			degenerate:int

			def __init__(self):
				self.triangle = (0, 0, 0) #4
				self.material = "" #4
				self.passable = 0 #4
				self.transparent = 0 #4
				self.collisionrequired = 0 #4
				self.culled = 0 #4
				self.degenerate = 0 #4

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
		records = property(r, "NUMMODELS", 1)
		nummodels = int(records[1])

		self.models = []
		for i in range(nummodels):
			modeli = type(self).model()
			records = property(r, "MODEL", 1)
			modeli.model = str(records[1])
			records = property(r, "MAINPIECE", 1)
			modeli.mainpiece = int(records[1])
			records = property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			modeli.vertices = []
			for j in range(numvertices):
				vertexj = type(modeli).vertex()
				property(r, "VERTEX", 0)

				records = property(r, "XYZ", 3)
				vertexj.xyz = (float(records[1]), float(records[2]), float(records[3]))
				records = property(r, "UV", 2)
				vertexj.uv = (float(records[1]), float(records[2]))
				records = property(r, "UV2", 2)
				vertexj.uv2 = (float(records[1]), float(records[2]))
				records = property(r, "NORMAL", 3)
				vertexj.normal = (float(records[1]), float(records[2]), float(records[3]))
				records = property(r, "TINT", 4)
				vertexj.tint = (int(records[1]), int(records[2]), int(records[3]), int(records[4]))
				records = property(r, "NUMWEIGHTS", 1)
				numweights = int(records[1])

				vertexj.weights = []
				for k in range(numweights):
					weightk = type(vertexj).weight()
					records = property(r, "WEIGHT", 2)
					weightk.weight = (int(records[1]), float(records[2]))
					vertexj.weights.append(weightk)
				modeli.vertices.append(vertexj)
			records = property(r, "NUMFACES", 1)
			numfaces = int(records[1])

			modeli.faces = []
			for j in range(numfaces):
				facej = type(modeli).face()
				property(r, "FACE", 0)

				records = property(r, "TRIANGLE", 3)
				facej.triangle = (int(records[1]), int(records[2]), int(records[3]))
				records = property(r, "MATERIAL", 1)
				facej.material = str(records[1])
				records = property(r, "PASSABLE", 1)
				facej.passable = int(records[1])
				records = property(r, "TRANSPARENT", 1)
				facej.transparent = int(records[1])
				records = property(r, "COLLISIONREQUIRED", 1)
				facej.collisionrequired = int(records[1])
				records = property(r, "CULLED", 1)
				facej.culled = int(records[1])
				records = property(r, "DEGENERATE", 1)
				facej.degenerate = int(records[1])
				modeli.faces.append(facej)
			self.models.append(modeli)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMMATERIALS {len(self.materials)}\n")
		for materialtagi in self.materials:
			w.write(f"\t\tMATERIALTAG \"{materialtagi.materialtag}\"\n")
			w.write(f"\t\tSHADERTAG \"{materialtagi.shadertag}\"\n")
			w.write(f"\t\tNUMPROPERTIES {len(materialtagi.properties)}\n")
			for propertyj in materialtagi.properties:
				w.write(f"\t\t\tPROPERTY {propertyj.property[0]} {propertyj.property[1]} {propertyj.property[2]}\n")
			w.write(f"\t\tANIMSLEEP {materialtagi.animsleep}\n")
			w.write(f"\t\tNUMANIMTEXTURES {len(materialtagi.animtextures)}\n")
			for texturej in materialtagi.animtextures:
				w.write(f"\t\t\tTEXTURE \"{texturej.texture}\"\n")
		w.write(f"\tNUMBONES {len(self.bones)}\n")
		for bonei in self.bones:
			w.write(f"\t\tBONE \"{bonei.bone}\"\n")
			w.write(f"\t\tNEXT {bonei.next}\n")
			w.write(f"\t\tCHILDREN {bonei.children}\n")
			w.write(f"\t\tCHILDINDEX {bonei.childindex}\n")
			w.write(f"\t\tPIVOT {format(bonei.pivot[0], '.8e')} {format(bonei.pivot[1], '.8e')} {format(bonei.pivot[2], '.8e')}\n")
			w.write(f"\t\tQUATERNION {format(bonei.quaternion[0], '.8e')} {format(bonei.quaternion[1], '.8e')} {format(bonei.quaternion[2], '.8e')} {format(bonei.quaternion[3], '.8e')}\n")
			w.write(f"\t\tSCALE {format(bonei.scale[0], '.8e')} {format(bonei.scale[1], '.8e')} {format(bonei.scale[2], '.8e')}\n")
		w.write(f"\tNUMMODELS {len(self.models)}\n")
		for modeli in self.models:
			w.write(f"\t\tMODEL \"{modeli.model}\"\n")
			w.write(f"\t\tMAINPIECE {modeli.mainpiece}\n")
			w.write(f"\t\tNUMVERTICES {len(modeli.vertices)}\n")
			for vertexj in modeli.vertices:
				w.write(f"\t\t\tVERTEX\n")
				w.write(f"\t\t\tXYZ {format(vertexj.xyz[0], '.8e')} {format(vertexj.xyz[1], '.8e')} {format(vertexj.xyz[2], '.8e')}\n")
				w.write(f"\t\t\tUV {format(vertexj.uv[0], '.8e')} {format(vertexj.uv[1], '.8e')}\n")
				w.write(f"\t\t\tUV2 {format(vertexj.uv2[0], '.8e')} {format(vertexj.uv2[1], '.8e')}\n")
				w.write(f"\t\t\tNORMAL {format(vertexj.normal[0], '.8e')} {format(vertexj.normal[1], '.8e')} {format(vertexj.normal[2], '.8e')}\n")
				w.write(f"\t\t\tTINT {vertexj.tint[0]} {vertexj.tint[1]} {vertexj.tint[2]} {vertexj.tint[3]}\n")
				w.write(f"\t\t\tNUMWEIGHTS {len(vertexj.weights)}\n")
				for weightk in vertexj.weights:
					w.write(f"\t\t\t\tWEIGHT {weightk.weight[0]} {format(weightk.weight[1], '.8e')}\n")
			w.write(f"\t\tNUMFACES {len(modeli.faces)}\n")
			for facej in modeli.faces:
				w.write(f"\t\t\tFACE\n")
				w.write(f"\t\t\tTRIANGLE {facej.triangle[0]} {facej.triangle[1]} {facej.triangle[2]}\n")
				w.write(f"\t\t\tMATERIAL \"{facej.material}\"\n")
				w.write(f"\t\t\tPASSABLE {facej.passable}\n")
				w.write(f"\t\t\tTRANSPARENT {facej.transparent}\n")
				w.write(f"\t\t\tCOLLISIONREQUIRED {facej.collisionrequired}\n")
				w.write(f"\t\t\tCULLED {facej.culled}\n")
				w.write(f"\t\t\tDEGENERATE {facej.degenerate}\n")
		return ""

