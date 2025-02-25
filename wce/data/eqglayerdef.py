# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class eqglayerdef:
	@staticmethod
	def definition():
		return "EQGLAYERDEF"

	tag:str
	version:int

	class layer:

		material:str

		diffuse:str

		normal:str

	layers:list[layer]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "VERSION", 1)
		self.version = int(records[1])
		records = parse.property(r, "NUMLAYERS", 1)
		numlayers = int(records[1])

		self.layers = []
		for i in range(numlayers):
			layeri = self.layer()
			parse.property(r, "LAYER", 0)

			records = parse.property(r, "MATERIAL", 1)
			layeri.material = str(records[1])
			records = parse.property(r, "DIFFUSE", 1)
			layeri.diffuse = str(records[1])
			records = parse.property(r, "NORMAL", 1)
			layeri.normal = str(records[1])
			self.layers.append(layeri)

	def write(self, w:io.TextIOWrapper):
		w.write(f"VERSION \"{self.version}\"\n")
		w.write(f"NUMLAYERS \"{len(self.layers)}\"\n")
		for layeri in self.layers:
			w.write(f"LAYER\n")
			w.write(f"MATERIAL \"{layeri.material}\"\n")
			w.write(f"DIFFUSE \"{layeri.diffuse}\"\n")
			w.write(f"NORMAL \"{layeri.normal}\"\n")

