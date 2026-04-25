# Generated from quail, DO NOT EDIT
import io
from .parse import property

class materialpalette:
	@staticmethod
	def definition():
		return "MATERIALPALETTE"

	tag:str

	def __init__(self):
		self.tag = ""
		self.materials = []

	class material:
		material:str

		def __init__(self):
			self.material = "" #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NUMMATERIALS", 1)
		nummaterials = int(records[1])

		self.materials = []
		for i in range(nummaterials):
			materiali = type(self).material()
			records = property(r, "MATERIAL", 1)
			materiali.material = str(records[1])
			self.materials.append(materiali)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMMATERIALS {len(self.materials)}\n")
		for materiali in self.materials:
			w.write(f"\t\tMATERIAL \"{materiali.material}\"\n")
		return ""

