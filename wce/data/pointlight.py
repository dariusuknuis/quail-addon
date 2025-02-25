# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

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
		records = parse.property(r, "LIGHT", 1)
		self.light = str(records[1])
		records = parse.property(r, "STATIC", 1)
		self.static = int(records[1])
		records = parse.property(r, "STATICINFLUENCE", 1)
		self.staticinfluence = str(records[1])
		records = parse.property(r, "HASREGIONS", 1)
		self.hasregions = int(records[1])
		records = parse.property(r, "XYZ", 3)
		self.xyz = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "RADIUSOFINFLUENCE", 1)
		self.radiusofinfluence = float(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"LIGHT \"{self.light}\"\n")
		w.write(f"STATIC \"{self.static}\"\n")
		w.write(f"STATICINFLUENCE \"{self.staticinfluence}\"\n")
		w.write(f"HASREGIONS \"{self.hasregions}\"\n")
		w.write(f"XYZ \"{self.xyz}\"\n")
		w.write(f"RADIUSOFINFLUENCE \"{self.radiusofinfluence}\"\n")

