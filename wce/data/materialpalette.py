# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class materialpalette:
	@staticmethod
	def definition():
		return "MATERIALPALETTE"

	tag:str

	class material:
		material:str # Material tag

	materials:list[material]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "NUMMATERIALS", 1)
		nummaterials = int(records[1])

		self.materials = []
		for i in range(nummaterials):
			materiali = self.material()
			records = parse.property(r, "MATERIAL", 1)
			materiali.material = str(records[1])
			self.materials.append(materiali)

	def write(self, w:io.TextIOWrapper):
		w.write(f"NUMMATERIALS \"{len(self.materials)}\"\n")
		for materiali in self.materials:
			w.write(f"MATERIAL \"{materiali.material}\"\n")

