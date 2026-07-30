# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqglit:
	@staticmethod
	def definition():
		return "EQGLIT"

	tag:str

	def __init__(self):
		self.tag = ""
		self.lits = []

	class lit:
		lit:tuple[int, int, int, int]

		def __init__(self):
			self.lit = (0, 0, 0, 0) #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NUMLITS", 1)
		numlits = int(records[1])

		self.lits = []
		for i in range(numlits):
			liti = type(self).lit()
			records = property(r, "LIT", 4)
			liti.lit = (int(records[1]), int(records[2]), int(records[3]), int(records[4]))
			self.lits.append(liti)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMLITS {len(self.lits)}\n")
		for liti in self.lits:
			w.write(f"\t\tLIT {liti.lit[0]} {liti.lit[1]} {liti.lit[2]} {liti.lit[3]}\n")
		return ""

