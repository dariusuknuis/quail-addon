# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class worlddef:
	@staticmethod
	def definition():
		return "WORLDDEF"

	newworld:int # Is this a new wld file?
	zone:str # Should this wce be treated like a zone?
	eqgversion:tuple[int, None] # Used in eqg parsing for version rebuilding

	def __init__(self, tag:str, r:io.TextIOWrapper):
		records = parse.property(r, "NEWWORLD", 1)
		self.newworld = int(records[1])
		records = parse.property(r, "ZONE", 1)
		self.zone = str(records[1])
		records = parse.property(r, "EQGVERSION?", 1)
		self.eqgversion = (int(records[1]) if records[1] != "NULL" else None)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()}\n")
		w.write(f"\tNEWWORLD \"{self.newworld}\"\n")
		w.write(f"\tZONE \"{self.zone}\"\n")
		w.write(f"\tEQGVERSION? \"{self.eqgversion}\"\n")

