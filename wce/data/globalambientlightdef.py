# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class globalambientlightdef:
	@staticmethod
	def definition():
		return "GLOBALAMBIENTLIGHTDEF"

	color:tuple[int, int, int, int] # Is this a new wld file?

	def __init__(self, tag:str, r:io.TextIOWrapper):
		records = parse.property(r, "COLOR", 4)
		self.color = int(records[1]), int(records[2]), int(records[3]), int(records[4])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()}\n")
		w.write(f"\tCOLOR \"{self.color}\"\n")

