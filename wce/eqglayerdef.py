# Generated from quail, DO NOT EDIT
import io
from .parse import property

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
		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMLAYERS", 1)
		numlayers = int(records[1])

		self.layers = []
		for i in range(numlayers):
			layeri = self.layer()
			property(r, "LAYER", 0)

			records = property(r, "MATERIAL", 1)
			layeri.material = str(records[1])
			records = property(r, "DIFFUSE", 1)
			layeri.diffuse = str(records[1])
			records = property(r, "NORMAL", 1)
			layeri.normal = str(records[1])
			self.layers.append(layeri)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMLAYERS \"{len(self.layers)}\"\n")
		for layeri in self.layers:
			w.write(f"\t\tLAYER\n")
			w.write(f"\t\tMATERIAL \"{layeri.material}\"\n")
			w.write(f"\t\tDIFFUSE \"{layeri.diffuse}\"\n")
			w.write(f"\t\tNORMAL \"{layeri.normal}\"\n")

