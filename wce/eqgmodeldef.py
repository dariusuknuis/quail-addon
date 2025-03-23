# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgmodeldef:
	@staticmethod
	def definition():
		return "EQGMODELDEF"

	tag:str
	version:int

	class material:
		material:str

		shadertag:str

		hexoneflag:int


		class property:
			property:tuple[str, int, str]

		propertys:list[property]

		animsleep:int


		class texture:
			texture:str

		textures:list[texture]

	materials:list[material]

	class vertex:

		xyz:tuple[float, float, float]

		uv:tuple[float, float]

		uv2:tuple[float, float]

		normal:tuple[float, float, float]

		tint:tuple[int, int, int, int]


		class weight:
			weight:tuple[int, float]

		weights:list[weight]

	vertexs:list[vertex]

	class face:

		triangle:tuple[int, int, int]

		material:str

		passable:int

		transparent:int

		collisionrequired:int

		culled:int

		degenerate:int

	faces:list[face]

	class bone:
		bone:str

		next:int

		children:int

		childindex:int

		pivot:tuple[float, float, float]

		quaternion:tuple[float, float, float, float]

		scale:tuple[float, float, float]

	bones:list[bone]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMMATERIALS", 1)
		nummaterials = int(records[1])

		self.materials = []
		for i in range(nummaterials):
			materiali = self.material()
			records = property(r, "MATERIAL", 1)
			materiali.material = str(records[1])
			records = property(r, "SHADERTAG", 1)
			materiali.shadertag = str(records[1])
			records = property(r, "HEXONEFLAG", 1)
			materiali.hexoneflag = int(records[1])
			records = property(r, "NUMPROPERTIES", 1)
			numproperties = int(records[1])

			materiali.propertys = []
			for j in range(numproperties):
				propertyj = self.material.property()
				records = property(r, "PROPERTY", 3)
				propertyj.property = str(records[1]), int(records[2]), str(records[3])
				materiali.propertys.append(propertyj)
			records = property(r, "ANIMSLEEP", 1)
			materiali.animsleep = int(records[1])
			records = property(r, "NUMANIMTEXTURES", 1)
			numanimtextures = int(records[1])

			materiali.textures = []
			for j in range(numanimtextures):
				texturej = self.material.texture()
				records = property(r, "TEXTURE", 1)
				texturej.texture = str(records[1])
				materiali.textures.append(texturej)
			self.materials.append(materiali)
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertexs = []
		for i in range(numvertices):
			vertexi = self.vertex()
			property(r, "VERTEX", 0)

			records = property(r, "XYZ", 3)
			vertexi.xyz = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "UV", 2)
			vertexi.uv = float(records[1]), float(records[2])
			records = property(r, "UV2", 2)
			vertexi.uv2 = float(records[1]), float(records[2])
			records = property(r, "NORMAL", 3)
			vertexi.normal = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "TINT", 4)
			vertexi.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			records = property(r, "NUMWEIGHTS", 1)
			numweights = int(records[1])

			vertexi.weights = []
			for j in range(numweights):
				weightj = self.vertex.weight()
				records = property(r, "WEIGHT", 2)
				weightj.weight = int(records[1]), float(records[2])
				vertexi.weights.append(weightj)
			self.vertexs.append(vertexi)
		records = property(r, "NUMFACES", 1)
		numfaces = int(records[1])

		self.faces = []
		for i in range(numfaces):
			facei = self.face()
			property(r, "FACE", 0)

			records = property(r, "TRIANGLE", 3)
			facei.triangle = int(records[1]), int(records[2]), int(records[3])
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
			bonei = self.bone()
			records = property(r, "BONE", 1)
			bonei.bone = str(records[1])
			records = property(r, "NEXT", 1)
			bonei.next = int(records[1])
			records = property(r, "CHILDREN", 1)
			bonei.children = int(records[1])
			records = property(r, "CHILDINDEX", 1)
			bonei.childindex = int(records[1])
			records = property(r, "PIVOT", 3)
			bonei.pivot = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "QUATERNION", 4)
			bonei.quaternion = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = property(r, "SCALE", 3)
			bonei.scale = float(records[1]), float(records[2]), float(records[3])
			self.bones.append(bonei)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMMATERIALS \"{len(self.materials)}\"\n")
		for materiali in self.materials:
			w.write(f"\t\tMATERIAL \"{materiali.material}\"\n")
			w.write(f"\t\tSHADERTAG \"{materiali.shadertag}\"\n")
			w.write(f"\t\tHEXONEFLAG \"{materiali.hexoneflag}\"\n")
			w.write(f"\t\tNUMPROPERTIES \"{len(materiali.propertys)}\"\n")
			for propertyj in materiali.propertys:
				w.write(f"\t\t\tPROPERTY \"{propertyj.property}\"\n")
			w.write(f"\t\tANIMSLEEP \"{materiali.animsleep}\"\n")
			w.write(f"\t\tNUMANIMTEXTURES \"{len(materiali.textures)}\"\n")
			for texturej in materiali.textures:
				w.write(f"\t\t\tTEXTURE \"{texturej.texture}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.vertexs)}\"\n")
		for vertexi in self.vertexs:
			w.write(f"\t\tVERTEX\n")
			w.write(f"\t\tXYZ \"{vertexi.xyz}\"\n")
			w.write(f"\t\tUV \"{vertexi.uv}\"\n")
			w.write(f"\t\tUV2 \"{vertexi.uv2}\"\n")
			w.write(f"\t\tNORMAL \"{vertexi.normal}\"\n")
			w.write(f"\t\tTINT \"{vertexi.tint}\"\n")
			w.write(f"\t\tNUMWEIGHTS \"{len(vertexi.weights)}\"\n")
			for weightj in vertexi.weights:
				w.write(f"\t\t\tWEIGHT \"{weightj.weight}\"\n")
		w.write(f"\tNUMFACES \"{len(self.faces)}\"\n")
		for facei in self.faces:
			w.write(f"\t\tFACE\n")
			w.write(f"\t\tTRIANGLE \"{facei.triangle}\"\n")
			w.write(f"\t\tMATERIAL \"{facei.material}\"\n")
			w.write(f"\t\tPASSABLE \"{facei.passable}\"\n")
			w.write(f"\t\tTRANSPARENT \"{facei.transparent}\"\n")
			w.write(f"\t\tCOLLISIONREQUIRED \"{facei.collisionrequired}\"\n")
			w.write(f"\t\tCULLED \"{facei.culled}\"\n")
			w.write(f"\t\tDEGENERATE \"{facei.degenerate}\"\n")
		w.write(f"\tNUMBONES \"{len(self.bones)}\"\n")
		for bonei in self.bones:
			w.write(f"\t\tBONE \"{bonei.bone}\"\n")
			w.write(f"\t\tNEXT \"{bonei.next}\"\n")
			w.write(f"\t\tCHILDREN \"{bonei.children}\"\n")
			w.write(f"\t\tCHILDINDEX \"{bonei.childindex}\"\n")
			w.write(f"\t\tPIVOT \"{bonei.pivot}\"\n")
			w.write(f"\t\tQUATERNION \"{bonei.quaternion}\"\n")
			w.write(f"\t\tSCALE \"{bonei.scale}\"\n")

