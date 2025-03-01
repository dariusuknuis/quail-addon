# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgterdef:
	@staticmethod
	def definition():
		return "EQGTERDEF"

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


		class vertex:

			xyz:tuple[float, float, float]

			uv:tuple[float, float]

			uv2:tuple[float, float]

			normal:tuple[float, float, float]

			tint:tuple[int, int, int, int]

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

			name:str

			next:int

			children:int

			childindex:int

			pivot:tuple[float, float, float]

			quaternion:tuple[float, float, float, float]

			scale:tuple[float, float, float]

		bones:list[bone]

	materials:list[material]

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
			records = property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			materiali.vertexs = []
			for j in range(numvertices):
				vertexj = self.material.vertex()
				property(r, "VERTEX", 0)

				records = property(r, "XYZ", 3)
				vertexj.xyz = float(records[1]), float(records[2]), float(records[3])
				records = property(r, "UV", 2)
				vertexj.uv = float(records[1]), float(records[2])
				records = property(r, "UV2", 2)
				vertexj.uv2 = float(records[1]), float(records[2])
				records = property(r, "NORMAL", 3)
				vertexj.normal = float(records[1]), float(records[2]), float(records[3])
				records = property(r, "TINT", 4)
				vertexj.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
				materiali.vertexs.append(vertexj)
			records = property(r, "NUMFACES", 1)
			numfaces = int(records[1])

			materiali.faces = []
			for j in range(numfaces):
				facej = self.material.face()
				property(r, "FACE", 0)

				records = property(r, "TRIANGLE", 3)
				facej.triangle = int(records[1]), int(records[2]), int(records[3])
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
				materiali.faces.append(facej)
			records = property(r, "NUMBONES", 1)
			numbones = int(records[1])

			materiali.bones = []
			for j in range(numbones):
				bonej = self.material.bone()
				property(r, "BONE", 0)

				records = property(r, "NAME", 1)
				bonej.name = str(records[1])
				records = property(r, "NEXT", 1)
				bonej.next = int(records[1])
				records = property(r, "CHILDREN", 1)
				bonej.children = int(records[1])
				records = property(r, "CHILDINDEX", 1)
				bonej.childindex = int(records[1])
				records = property(r, "PIVOT", 3)
				bonej.pivot = float(records[1]), float(records[2]), float(records[3])
				records = property(r, "QUATERNION", 4)
				bonej.quaternion = float(records[1]), float(records[2]), float(records[3]), float(records[4])
				records = property(r, "SCALE", 3)
				bonej.scale = float(records[1]), float(records[2]), float(records[3])
				materiali.bones.append(bonej)
			self.materials.append(materiali)

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
			w.write(f"\t\tNUMVERTICES \"{len(materiali.vertexs)}\"\n")
			for vertexj in materiali.vertexs:
				w.write(f"\t\t\tVERTEX\n")
				w.write(f"\t\t\tXYZ \"{vertexj.xyz}\"\n")
				w.write(f"\t\t\tUV \"{vertexj.uv}\"\n")
				w.write(f"\t\t\tUV2 \"{vertexj.uv2}\"\n")
				w.write(f"\t\t\tNORMAL \"{vertexj.normal}\"\n")
				w.write(f"\t\t\tTINT \"{vertexj.tint}\"\n")
			w.write(f"\t\tNUMFACES \"{len(materiali.faces)}\"\n")
			for facej in materiali.faces:
				w.write(f"\t\t\tFACE\n")
				w.write(f"\t\t\tTRIANGLE \"{facej.triangle}\"\n")
				w.write(f"\t\t\tMATERIAL \"{facej.material}\"\n")
				w.write(f"\t\t\tPASSABLE \"{facej.passable}\"\n")
				w.write(f"\t\t\tTRANSPARENT \"{facej.transparent}\"\n")
				w.write(f"\t\t\tCOLLISIONREQUIRED \"{facej.collisionrequired}\"\n")
				w.write(f"\t\t\tCULLED \"{facej.culled}\"\n")
				w.write(f"\t\t\tDEGENERATE \"{facej.degenerate}\"\n")
			w.write(f"\t\tNUMBONES \"{len(materiali.bones)}\"\n")
			for bonej in materiali.bones:
				w.write(f"\t\t\tBONE\n")
				w.write(f"\t\t\tNAME \"{bonej.name}\"\n")
				w.write(f"\t\t\tNEXT \"{bonej.next}\"\n")
				w.write(f"\t\t\tCHILDREN \"{bonej.children}\"\n")
				w.write(f"\t\t\tCHILDINDEX \"{bonej.childindex}\"\n")
				w.write(f"\t\t\tPIVOT \"{bonej.pivot}\"\n")
				w.write(f"\t\t\tQUATERNION \"{bonej.quaternion}\"\n")
				w.write(f"\t\t\tSCALE \"{bonej.scale}\"\n")

