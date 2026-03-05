# Generated from quail, DO NOT EDIT
import io
from .parse import property

class zone:
	@staticmethod
	def definition():
		return "ZONE"

	tag:str
	regionlist:list[str]
	userdata:str

	def __init__(self):
		self.tag = ""
		self.regionlist = list[str] #2
		self.userdata = "" #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "REGIONLIST", -1)
		self.regionlist = records[1:]

		records = property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tREGIONLIST \"{self.regionlist}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		return ""

