# Generated from quail, DO NOT EDIT
import io
from .parse import property

class ambientlight:
	@staticmethod
	def definition():
		return "AMBIENTLIGHT"

	tag:str
	light:str
	regionlist:list[str]

	def __init__(self):
		self.tag = ""
		self.light = "" #2
		self.regionlist = [] #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "LIGHT", 1)
		self.light = str(records[1])
		records = property(r, "REGIONLIST", -1)
		self.regionlist = records[1:]

		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tLIGHT \"{self.light}\"\n")
		w.write(f"\tREGIONLIST {self.regionlist}\n")
		return ""

