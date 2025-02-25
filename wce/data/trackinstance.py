# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class trackinstance:
	@staticmethod
	def definition():
		return "TRACKINSTANCE"

	tag:str
	tagindex:int
	definition:str
	definitionindex:int
	interpolate:int # deprecated, ignored in RoF2
	reverse:int # deprecated, ignored in RoF2
	sleep:tuple[int, None]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "DEFINITION", 1)
		self.definition = str(records[1])
		records = parse.property(r, "DEFINITIONINDEX", 1)
		self.definitionindex = int(records[1])
		records = parse.property(r, "INTERPOLATE", 1)
		self.interpolate = int(records[1])
		records = parse.property(r, "REVERSE", 1)
		self.reverse = int(records[1])
		records = parse.property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)

	def write(self, w:io.TextIOWrapper):
		w.write(f"TAGINDEX \"{self.tagindex}\"\n")
		w.write(f"DEFINITION \"{self.definition}\"\n")
		w.write(f"DEFINITIONINDEX \"{self.definitionindex}\"\n")
		w.write(f"INTERPOLATE \"{self.interpolate}\"\n")
		w.write(f"REVERSE \"{self.reverse}\"\n")
		w.write(f"SLEEP? \"{self.sleep}\"\n")

