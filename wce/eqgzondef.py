# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgzondef:
	@staticmethod
	def definition():
		return "EQGZONDEF"

	tag:str
	version:int

	class model:
		model:str

	models:list[model]

	class modeltag:
		modeltag:str

		instancetag:str

		translation:tuple[float, float, float]

		rotation:tuple[float, float, float]

		scale:float


		class lit:
			lit:int

		lits:list[lit]

	modeltags:list[modeltag]

	class area:
		area:str

		position:tuple[float, float, float]

		color:tuple[float, float, float]

		extents:tuple[float, float, float]

	areas:list[area]

	class light:
		light:str

		lightpos:tuple[float, float, float]

		lightcolor:tuple[float, float, float]

		lightradius:float

	lights:list[light]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMMODELS", 1)
		nummodels = int(records[1])

		self.models = []
		for i in range(nummodels):
			modeli = self.model()
			records = property(r, "MODEL", 1)
			modeli.model = str(records[1])
			self.models.append(modeli)
		records = property(r, "NUMINSTANCES", 1)
		numinstances = int(records[1])

		self.modeltags = []
		for i in range(numinstances):
			modeltagi = self.modeltag()
			records = property(r, "MODELTAG", 1)
			modeltagi.modeltag = str(records[1])
			records = property(r, "INSTANCETAG", 1)
			modeltagi.instancetag = str(records[1])
			records = property(r, "TRANSLATION", 3)
			modeltagi.translation = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "ROTATION", 3)
			modeltagi.rotation = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "SCALE", 1)
			modeltagi.scale = float(records[1])
			records = property(r, "NUMLITS", 1)
			numlits = int(records[1])

			modeltagi.lits = []
			for j in range(numlits):
				litj = self.modeltag.lit()
				records = property(r, "LIT", 1)
				litj.lit = int(records[1])
				modeltagi.lits.append(litj)
			self.modeltags.append(modeltagi)
		records = property(r, "NUMAREAS", 1)
		numareas = int(records[1])

		self.areas = []
		for i in range(numareas):
			areai = self.area()
			records = property(r, "AREA", 1)
			areai.area = str(records[1])
			records = property(r, "POSITION", 3)
			areai.position = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "COLOR", 3)
			areai.color = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "EXTENTS", 3)
			areai.extents = float(records[1]), float(records[2]), float(records[3])
			self.areas.append(areai)
		records = property(r, "NUMLIGHTS", 1)
		numlights = int(records[1])

		self.lights = []
		for i in range(numlights):
			lighti = self.light()
			records = property(r, "LIGHT", 1)
			lighti.light = str(records[1])
			records = property(r, "LIGHTPOS", 3)
			lighti.lightpos = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "LIGHTCOLOR", 3)
			lighti.lightcolor = float(records[1]), float(records[2]), float(records[3])
			records = property(r, "LIGHTRADIUS", 1)
			lighti.lightradius = float(records[1])
			self.lights.append(lighti)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMMODELS \"{len(self.models)}\"\n")
		for modeli in self.models:
			w.write(f"\t\tMODEL \"{modeli.model}\"\n")
		w.write(f"\tNUMINSTANCES \"{len(self.modeltags)}\"\n")
		for modeltagi in self.modeltags:
			w.write(f"\t\tMODELTAG \"{modeltagi.modeltag}\"\n")
			w.write(f"\t\tINSTANCETAG \"{modeltagi.instancetag}\"\n")
			w.write(f"\t\tTRANSLATION \"{modeltagi.translation}\"\n")
			w.write(f"\t\tROTATION \"{modeltagi.rotation}\"\n")
			w.write(f"\t\tSCALE \"{modeltagi.scale}\"\n")
			w.write(f"\t\tNUMLITS \"{len(modeltagi.lits)}\"\n")
			for litj in modeltagi.lits:
				w.write(f"\t\t\tLIT \"{litj.lit}\"\n")
		w.write(f"\tNUMAREAS \"{len(self.areas)}\"\n")
		for areai in self.areas:
			w.write(f"\t\tAREA \"{areai.area}\"\n")
			w.write(f"\t\tPOSITION \"{areai.position}\"\n")
			w.write(f"\t\tCOLOR \"{areai.color}\"\n")
			w.write(f"\t\tEXTENTS \"{areai.extents}\"\n")
		w.write(f"\tNUMLIGHTS \"{len(self.lights)}\"\n")
		for lighti in self.lights:
			w.write(f"\t\tLIGHT \"{lighti.light}\"\n")
			w.write(f"\t\tLIGHTPOS \"{lighti.lightpos}\"\n")
			w.write(f"\t\tLIGHTCOLOR \"{lighti.lightcolor}\"\n")
			w.write(f"\t\tLIGHTRADIUS \"{lighti.lightradius}\"\n")

