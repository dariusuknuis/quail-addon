# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class ambientlight:
	@staticmethod
	def definition():
		return "AMBIENTLIGHT"

	tag:str
	light:float
	regionlist:list[str]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "LIGHT", 1)
		self.light = float(records[1])
		records = parse.property(r, "REGIONLIST", -1)
		self.regionlist = records[1:]


	def write(self, w:io.TextIOWrapper):
		w.write(f"LIGHT \"{self.light}\"\n")
		w.write(f"REGIONLIST \"{self.regionlist}\"\n")

