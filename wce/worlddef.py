# Generated from quail, DO NOT EDIT
import io
from .parse import property

class worlddef:
	@staticmethod
	def definition():
		return "WORLDDEF"

	newworld:int
	zone:str
	eqgversion:tuple[int, None]

	def __init__(self):
		self.newworld = 0 #2
		self.zone = "" #2
		self.eqgversion = tuple[int, None] #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		if r is None:
			return "no reader provided"

		records = property(r, "NEWWORLD", 1)
		self.newworld = int(records[1])
		records = property(r, "ZONE", 1)
		self.zone = str(records[1])
		records = property(r, "EQGVERSION?", 1)
		self.eqgversion = (int(records[1]) if records[1] != "NULL" else None)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()}\n")
		w.write(f"\tNEWWORLD \"{self.newworld}\"\n")
		w.write(f"\tZONE \"{self.zone}\"\n")
		w.write(f"\tEQGVERSION? \"{self.eqgversion}\"\n")
		return ""

