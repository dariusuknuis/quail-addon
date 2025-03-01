# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgskinnedmodeldef:
	@staticmethod
	def definition():
		return "EQGSKINNEDMODELDEF"

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


		class bone:
			bone:str

			next:int

			children:int

			childindex:int

			pivot:tuple[float, float, float]

			quaternion:tuple[float, float, float, float]

			scale:tuple[float, float, float]

		bones:list[bone]


		class model:
			model:str

			mainpiece:int


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


			class weight:
				weight:tuple[int, float, int, float, int, float, int, float]

			weights:list[weight]

		models:list[model]

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
			records = property(r, "NUMBONES", 1)
			numbones = int(records[1])

			materiali.bones = []
			for j in range(numbones):
				bonej = self.material.bone()
				records = property(r, "BONE", 1)
				bonej.bone = str(records[1])
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
			records = property(r, "NUMMODELS", 1)
			nummodels = int(records[1])

			materiali.models = []
			for j in range(nummodels):
				modelj = self.material.model()
				records = property(r, "MODEL", 1)
				modelj.model = str(records[1])
				records = property(r, "MAINPIECE", 1)
				modelj.mainpiece = int(records[1])
				records = property(r, "NUMVERTICES", 1)
				numvertices = int(records[1])

				modelj.vertexs = []
				for k in range(numvertices):
					vertexk = self.material.model.vertex()
					property(r, "VERTEX", 0)

					records = property(r, "XYZ", 3)
					vertexk.xyz = float(records[1]), float(records[2]), float(records[3])
					records = property(r, "UV", 2)
					vertexk.uv = float(records[1]), float(records[2])
					records = property(r, "UV2", 2)
					vertexk.uv2 = float(records[1]), float(records[2])
					records = property(r, "NORMAL", 3)
					vertexk.normal = float(records[1]), float(records[2]), float(records[3])
					records = property(r, "TINT", 4)
					vertexk.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
					modelj.vertexs.append(vertexk)
				records = property(r, "NUMFACES", 1)
				numfaces = int(records[1])

				modelj.faces = []
				for k in range(numfaces):
					facek = self.material.model.face()
					property(r, "FACE", 0)

					records = property(r, "TRIANGLE", 3)
					facek.triangle = int(records[1]), int(records[2]), int(records[3])
					records = property(r, "MATERIAL", 1)
					facek.material = str(records[1])
					records = property(r, "PASSABLE", 1)
					facek.passable = int(records[1])
					records = property(r, "TRANSPARENT", 1)
					facek.transparent = int(records[1])
					records = property(r, "COLLISIONREQUIRED", 1)
					facek.collisionrequired = int(records[1])
					records = property(r, "CULLED", 1)
					facek.culled = int(records[1])
					records = property(r, "DEGENERATE", 1)
					facek.degenerate = int(records[1])
					modelj.faces.append(facek)
				records = property(r, "NUMWEIGHTS", 1)
				numweights = int(records[1])

				modelj.weights = []
				for k in range(numweights):
					weightk = self.material.model.weight()
					records = property(r, "WEIGHT", 8)
					weightk.weight = int(records[1]), float(records[2]), int(records[3]), float(records[4]), int(records[5]), float(records[6]), int(records[7]), float(records[8])
					modelj.weights.append(weightk)
				materiali.models.append(modelj)
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
			w.write(f"\t\tNUMBONES \"{len(materiali.bones)}\"\n")
			for bonej in materiali.bones:
				w.write(f"\t\t\tBONE \"{bonej.bone}\"\n")
				w.write(f"\t\t\tNEXT \"{bonej.next}\"\n")
				w.write(f"\t\t\tCHILDREN \"{bonej.children}\"\n")
				w.write(f"\t\t\tCHILDINDEX \"{bonej.childindex}\"\n")
				w.write(f"\t\t\tPIVOT \"{bonej.pivot}\"\n")
				w.write(f"\t\t\tQUATERNION \"{bonej.quaternion}\"\n")
				w.write(f"\t\t\tSCALE \"{bonej.scale}\"\n")
			w.write(f"\t\tNUMMODELS \"{len(materiali.models)}\"\n")
			for modelj in materiali.models:
				w.write(f"\t\t\tMODEL \"{modelj.model}\"\n")
				w.write(f"\t\t\tMAINPIECE \"{modelj.mainpiece}\"\n")
				w.write(f"\t\t\tNUMVERTICES \"{len(modelj.vertexs)}\"\n")
				for vertexk in modelj.vertexs:
					w.write(f"\t\t\t\tVERTEX\n")
					w.write(f"\t\t\t\tXYZ \"{vertexk.xyz}\"\n")
					w.write(f"\t\t\t\tUV \"{vertexk.uv}\"\n")
					w.write(f"\t\t\t\tUV2 \"{vertexk.uv2}\"\n")
					w.write(f"\t\t\t\tNORMAL \"{vertexk.normal}\"\n")
					w.write(f"\t\t\t\tTINT \"{vertexk.tint}\"\n")
				w.write(f"\t\t\tNUMFACES \"{len(modelj.faces)}\"\n")
				for facek in modelj.faces:
					w.write(f"\t\t\t\tFACE\n")
					w.write(f"\t\t\t\tTRIANGLE \"{facek.triangle}\"\n")
					w.write(f"\t\t\t\tMATERIAL \"{facek.material}\"\n")
					w.write(f"\t\t\t\tPASSABLE \"{facek.passable}\"\n")
					w.write(f"\t\t\t\tTRANSPARENT \"{facek.transparent}\"\n")
					w.write(f"\t\t\t\tCOLLISIONREQUIRED \"{facek.collisionrequired}\"\n")
					w.write(f"\t\t\t\tCULLED \"{facek.culled}\"\n")
					w.write(f"\t\t\t\tDEGENERATE \"{facek.degenerate}\"\n")
				w.write(f"\t\t\tNUMWEIGHTS \"{len(modelj.weights)}\"\n")
				for weightk in modelj.weights:
					w.write(f"\t\t\t\tWEIGHT \"{weightk.weight}\"\n")

