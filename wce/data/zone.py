# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class zone:
	@staticmethod
	def definition():
		return "ZONE"

	tag:str
	regionlist:list[str]
	userdata:str

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "REGIONLIST", -1)
		self.regionlist = records[1:]

		records = parse.property(r, "USERDATA", 1)
		self.userdata = str(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"REGIONLIST \"{self.regionlist}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")

