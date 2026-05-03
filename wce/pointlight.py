# Generated from quail, DO NOT EDIT
import io
from .parse import property

class pointlight:
	@staticmethod
	def definition():
		return "POINTLIGHT"

	tag:str
	light:str
	static:int
	staticinfluence:int
	dynamicinfluence:int
	xyz:tuple[float, float, float]
	radiusofinfluence:float
	regions:list[str] | None

	def __init__(self):
		self.tag = ""
		self.light = "" #2
		self.static = 0 #2
		self.staticinfluence = 0 #2
		self.dynamicinfluence = 0 #2
		self.xyz = (0.0, 0.0, 0.0) #2
		self.radiusofinfluence = 0.0 #2
		self.regions = None #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "LIGHT", 1)
		self.light = str(records[1])
		records = property(r, "STATIC", 1)
		self.static = int(records[1])
		records = property(r, "STATICINFLUENCE", 1)
		self.staticinfluence = int(records[1])
		records = property(r, "DYNAMICINFLUENCE", 1)
		self.dynamicinfluence = int(records[1])
		records = property(r, "XYZ", 3)
		self.xyz = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "RADIUSOFINFLUENCE", 1)
		self.radiusofinfluence = float(records[1])
		records = property(r, "REGIONS?", -1)
		self.regions = None if len(records) > 1 and records[1] == "NULL" else records[1:]

		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tLIGHT \"{self.light}\"\n")
		w.write(f"\tSTATIC {self.static}\n")
		w.write(f"\tSTATICINFLUENCE {self.staticinfluence}\n")
		w.write(f"\tDYNAMICINFLUENCE {self.dynamicinfluence}\n")
		w.write(f"\tXYZ {format(self.xyz[0], '.8e')} {format(self.xyz[1], '.8e')} {format(self.xyz[2], '.8e')}\n")
		w.write(f"\tRADIUSOFINFLUENCE {format(self.radiusofinfluence, '.8e')}\n")
		w.write(f"\tREGIONS? {'NULL' if self.regions is None else ' '.join(self.regions)}\n")
		return ""

