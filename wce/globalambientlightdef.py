# Generated from quail, DO NOT EDIT
import io
from .parse import property

class globalambientlightdef:
	@staticmethod
	def definition():
		return "GLOBALAMBIENTLIGHTDEF"

	color:tuple[int, int, int, int]

	def __init__(self):
		self.color = (0, 0, 0, 0) #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		if r is None:
			return "no reader provided"

		records = property(r, "COLOR", 4)
		self.color = (int(records[1]), int(records[2]), int(records[3]), int(records[4]))
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()}\n")
		w.write(f"\tCOLOR {self.color[0]} {self.color[1]} {self.color[2]} {self.color[3]}\n")
		return ""

