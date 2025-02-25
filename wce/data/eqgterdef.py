# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

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
		records = parse.property(r, "VERSION", 1)
		self.version = int(records[1])
		records = parse.property(r, "NUMMATERIALS", 1)
		nummaterials = int(records[1])

		self.materials = []
		for i in range(nummaterials):
			materiali = self.material()
			records = parse.property(r, "MATERIAL", 1)
			materiali.material = str(records[1])
			records = parse.property(r, "SHADERTAG", 1)
			materiali.shadertag = str(records[1])
			records = parse.property(r, "HEXONEFLAG", 1)
			materiali.hexoneflag = int(records[1])
			records = parse.property(r, "NUMPROPERTIES", 1)
			numproperties = int(records[1])

			materiali.propertys = []
			for j in range(numproperties):
				propertyj = self.material.property()
				records = parse.property(r, "PROPERTY", 3)
				propertyj.property = str(records[1]), int(records[2]), str(records[3])
				materiali.propertys.append(propertyj)
			records = parse.property(r, "ANIMSLEEP", 1)
			materiali.animsleep = int(records[1])
			records = parse.property(r, "NUMANIMTEXTURES", 1)
			numanimtextures = int(records[1])

			materiali.textures = []
			for j in range(numanimtextures):
				texturej = self.material.texture()
				records = parse.property(r, "TEXTURE", 1)
				texturej.texture = str(records[1])
				materiali.textures.append(texturej)
			records = parse.property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			materiali.vertexs = []
			for j in range(numvertices):
				vertexj = self.material.vertex()
				parse.property(r, "VERTEX", 0)

				records = parse.property(r, "XYZ", 3)
				vertexj.xyz = float(records[1]), float(records[2]), float(records[3])
				records = parse.property(r, "UV", 2)
				vertexj.uv = float(records[1]), float(records[2])
				records = parse.property(r, "UV2", 2)
				vertexj.uv2 = float(records[1]), float(records[2])
				records = parse.property(r, "NORMAL", 3)
				vertexj.normal = float(records[1]), float(records[2]), float(records[3])
				records = parse.property(r, "TINT", 4)
				vertexj.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
				materiali.vertexs.append(vertexj)
			records = parse.property(r, "NUMFACES", 1)
			numfaces = int(records[1])

			materiali.faces = []
			for j in range(numfaces):
				facej = self.material.face()
				parse.property(r, "FACE", 0)

				records = parse.property(r, "TRIANGLE", 3)
				facej.triangle = int(records[1]), int(records[2]), int(records[3])
				records = parse.property(r, "MATERIAL", 1)
				facej.material = str(records[1])
				records = parse.property(r, "PASSABLE", 1)
				facej.passable = int(records[1])
				records = parse.property(r, "TRANSPARENT", 1)
				facej.transparent = int(records[1])
				records = parse.property(r, "COLLISIONREQUIRED", 1)
				facej.collisionrequired = int(records[1])
				records = parse.property(r, "CULLED", 1)
				facej.culled = int(records[1])
				records = parse.property(r, "DEGENERATE", 1)
				facej.degenerate = int(records[1])
				materiali.faces.append(facej)
			records = parse.property(r, "NUMBONES", 1)
			numbones = int(records[1])

			materiali.bones = []
			for j in range(numbones):
				bonej = self.material.bone()
				parse.property(r, "BONE", 0)

				records = parse.property(r, "NAME", 1)
				bonej.name = str(records[1])
				records = parse.property(r, "NEXT", 1)
				bonej.next = int(records[1])
				records = parse.property(r, "CHILDREN", 1)
				bonej.children = int(records[1])
				records = parse.property(r, "CHILDINDEX", 1)
				bonej.childindex = int(records[1])
				records = parse.property(r, "PIVOT", 3)
				bonej.pivot = float(records[1]), float(records[2]), float(records[3])
				records = parse.property(r, "QUATERNION", 4)
				bonej.quaternion = float(records[1]), float(records[2]), float(records[3]), float(records[4])
				records = parse.property(r, "SCALE", 3)
				bonej.scale = float(records[1]), float(records[2]), float(records[3])
				materiali.bones.append(bonej)
			self.materials.append(materiali)

	def write(self, w:io.TextIOWrapper):
		w.write(f"VERSION \"{self.version}\"\n")
		w.write(f"NUMMATERIALS \"{len(self.materials)}\"\n")
		for materiali in self.materials:
			w.write(f"MATERIAL \"{materiali.material}\"\n")
			w.write(f"SHADERTAG \"{materiali.shadertag}\"\n")
			w.write(f"HEXONEFLAG \"{materiali.hexoneflag}\"\n")
			w.write(f"NUMPROPERTIES \"{len(materiali.propertys)}\"\n")
			for propertyj in materiali.propertys:
				w.write(f"PROPERTY \"{propertyj.property}\"\n")
			w.write(f"ANIMSLEEP \"{materiali.animsleep}\"\n")
			w.write(f"NUMANIMTEXTURES \"{len(materiali.textures)}\"\n")
			for texturej in materiali.textures:
				w.write(f"TEXTURE \"{texturej.texture}\"\n")
			w.write(f"NUMVERTICES \"{len(materiali.vertexs)}\"\n")
			for vertexj in materiali.vertexs:
				w.write(f"VERTEX\n")
				w.write(f"XYZ \"{vertexj.xyz}\"\n")
				w.write(f"UV \"{vertexj.uv}\"\n")
				w.write(f"UV2 \"{vertexj.uv2}\"\n")
				w.write(f"NORMAL \"{vertexj.normal}\"\n")
				w.write(f"TINT \"{vertexj.tint}\"\n")
			w.write(f"NUMFACES \"{len(materiali.faces)}\"\n")
			for facej in materiali.faces:
				w.write(f"FACE\n")
				w.write(f"TRIANGLE \"{facej.triangle}\"\n")
				w.write(f"MATERIAL \"{facej.material}\"\n")
				w.write(f"PASSABLE \"{facej.passable}\"\n")
				w.write(f"TRANSPARENT \"{facej.transparent}\"\n")
				w.write(f"COLLISIONREQUIRED \"{facej.collisionrequired}\"\n")
				w.write(f"CULLED \"{facej.culled}\"\n")
				w.write(f"DEGENERATE \"{facej.degenerate}\"\n")
			w.write(f"NUMBONES \"{len(materiali.bones)}\"\n")
			for bonej in materiali.bones:
				w.write(f"BONE\n")
				w.write(f"NAME \"{bonej.name}\"\n")
				w.write(f"NEXT \"{bonej.next}\"\n")
				w.write(f"CHILDREN \"{bonej.children}\"\n")
				w.write(f"CHILDINDEX \"{bonej.childindex}\"\n")
				w.write(f"PIVOT \"{bonej.pivot}\"\n")
				w.write(f"QUATERNION \"{bonej.quaternion}\"\n")
				w.write(f"SCALE \"{bonej.scale}\"\n")

