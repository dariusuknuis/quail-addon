# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgzondef:
	@staticmethod
	def definition():
		return "EQGZONDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.models = []
		self.instances = []
		self.areas = []
		self.lights = []

	class model:
		model:str

		def __init__(self):
			self.model = "" #3

	class modeltag:
		modeltag:str
		instancetag:str
		translation:tuple[float, float, float]
		rotation:tuple[float, float, float]
		scale:float

		def __init__(self):
			self.modeltag = "" #3
			self.instancetag = "" #3
			self.translation = (0.0, 0.0, 0.0) #3
			self.rotation = (0.0, 0.0, 0.0) #3
			self.scale = 0.0 #3
			self.lits = []

		class lit:
			lit:int

			def __init__(self):
				self.lit = 0 #4

	class area:
		area:str
		position:tuple[float, float, float]
		color:tuple[float, float, float]
		extents:tuple[float, float, float]

		def __init__(self):
			self.area = "" #3
			self.position = (0.0, 0.0, 0.0) #3
			self.color = (0.0, 0.0, 0.0) #3
			self.extents = (0.0, 0.0, 0.0) #3

	class light:
		light:str
		lightpos:tuple[float, float, float]
		lightcolor:tuple[float, float, float]
		lightradius:float

		def __init__(self):
			self.light = "" #3
			self.lightpos = (0.0, 0.0, 0.0) #3
			self.lightcolor = (0.0, 0.0, 0.0) #3
			self.lightradius = 0.0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMMODELS", 1)
		nummodels = int(records[1])

		self.models = []
		for i in range(nummodels):
			modeli = type(self).model()
			records = property(r, "MODEL", 1)
			modeli.model = str(records[1])
			self.models.append(modeli)
		records = property(r, "NUMINSTANCES", 1)
		numinstances = int(records[1])

		self.instances = []
		for i in range(numinstances):
			modeltagi = type(self).modeltag()
			records = property(r, "MODELTAG", 1)
			modeltagi.modeltag = str(records[1])
			records = property(r, "INSTANCETAG", 1)
			modeltagi.instancetag = str(records[1])
			records = property(r, "TRANSLATION", 3)
			modeltagi.translation = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "ROTATION", 3)
			modeltagi.rotation = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "SCALE", 1)
			modeltagi.scale = float(records[1])
			records = property(r, "NUMLITS", 1)
			numlits = int(records[1])

			modeltagi.lits = []
			for j in range(numlits):
				litj = type(modeltagi).lit()
				records = property(r, "LIT", 1)
				litj.lit = int(records[1])
				modeltagi.lits.append(litj)
			self.instances.append(modeltagi)
		records = property(r, "NUMAREAS", 1)
		numareas = int(records[1])

		self.areas = []
		for i in range(numareas):
			areai = type(self).area()
			records = property(r, "AREA", 1)
			areai.area = str(records[1])
			records = property(r, "POSITION", 3)
			areai.position = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "COLOR", 3)
			areai.color = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "EXTENTS", 3)
			areai.extents = (float(records[1]), float(records[2]), float(records[3]))
			self.areas.append(areai)
		records = property(r, "NUMLIGHTS", 1)
		numlights = int(records[1])

		self.lights = []
		for i in range(numlights):
			lighti = type(self).light()
			records = property(r, "LIGHT", 1)
			lighti.light = str(records[1])
			records = property(r, "LIGHTPOS", 3)
			lighti.lightpos = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "LIGHTCOLOR", 3)
			lighti.lightcolor = (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "LIGHTRADIUS", 1)
			lighti.lightradius = float(records[1])
			self.lights.append(lighti)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMMODELS \"{len(self.models)}\"\n")
		for modeli in self.models:
			w.write(f"\t\tMODEL \"{modeli.model}\"\n")
		w.write(f"\tNUMINSTANCES \"{len(self.instances)}\"\n")
		for modeltagi in self.instances:
			w.write(f"\t\tMODELTAG \"{modeltagi.modeltag}\"\n")
			w.write(f"\t\tINSTANCETAG \"{modeltagi.instancetag}\"\n")
			w.write(f"\t\tTRANSLATION {modeltagi.translation[0]} {modeltagi.translation[1]} {modeltagi.translation[2]}\n")
			w.write(f"\t\tROTATION {modeltagi.rotation[0]} {modeltagi.rotation[1]} {modeltagi.rotation[2]}\n")
			w.write(f"\t\tSCALE {modeltagi.scale}\n")
			w.write(f"\t\tNUMLITS \"{len(modeltagi.lits)}\"\n")
			for litj in modeltagi.lits:
				w.write(f"\t\t\tLIT {litj.lit}\n")
		w.write(f"\tNUMAREAS \"{len(self.areas)}\"\n")
		for areai in self.areas:
			w.write(f"\t\tAREA \"{areai.area}\"\n")
			w.write(f"\t\tPOSITION {areai.position[0]} {areai.position[1]} {areai.position[2]}\n")
			w.write(f"\t\tCOLOR {areai.color[0]} {areai.color[1]} {areai.color[2]}\n")
			w.write(f"\t\tEXTENTS {areai.extents[0]} {areai.extents[1]} {areai.extents[2]}\n")
		w.write(f"\tNUMLIGHTS \"{len(self.lights)}\"\n")
		for lighti in self.lights:
			w.write(f"\t\tLIGHT \"{lighti.light}\"\n")
			w.write(f"\t\tLIGHTPOS {lighti.lightpos[0]} {lighti.lightpos[1]} {lighti.lightpos[2]}\n")
			w.write(f"\t\tLIGHTCOLOR {lighti.lightcolor[0]} {lighti.lightcolor[1]} {lighti.lightcolor[2]}\n")
			w.write(f"\t\tLIGHTRADIUS {lighti.lightradius}\n")
		return ""

