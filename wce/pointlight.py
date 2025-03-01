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
	staticinfluence:str
	hasregions:int
	xyz:tuple[float, float, float]
	radiusofinfluence:float

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "LIGHT", 1)
		self.light = str(records[1])
		records = property(r, "STATIC", 1)
		self.static = int(records[1])
		records = property(r, "STATICINFLUENCE", 1)
		self.staticinfluence = str(records[1])
		records = property(r, "HASREGIONS", 1)
		self.hasregions = int(records[1])
		records = property(r, "XYZ", 3)
		self.xyz = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "RADIUSOFINFLUENCE", 1)
		self.radiusofinfluence = float(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tLIGHT \"{self.light}\"\n")
		w.write(f"\tSTATIC \"{self.static}\"\n")
		w.write(f"\tSTATICINFLUENCE \"{self.staticinfluence}\"\n")
		w.write(f"\tHASREGIONS \"{self.hasregions}\"\n")
		w.write(f"\tXYZ \"{self.xyz}\"\n")
		w.write(f"\tRADIUSOFINFLUENCE \"{self.radiusofinfluence}\"\n")

