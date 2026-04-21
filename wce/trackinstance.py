# Generated from quail, DO NOT EDIT
import io
from .parse import property

class trackinstance:
	@staticmethod
	def definition():
		return "TRACKINSTANCE"

	tag:str
	trackdef:str
	interpolate:int
	reverse:int
	sleep:int | None

	def __init__(self):
		self.tag = ""
		self.trackdef = "" #2
		self.interpolate = 0 #2
		self.reverse = 0 #2
		self.sleep = None #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "TRACKDEF", 1)
		self.trackdef = str(records[1])
		records = property(r, "INTERPOLATE", 1)
		self.interpolate = int(records[1])
		records = property(r, "REVERSE", 1)
		self.reverse = int(records[1])
		records = property(r, "SLEEP?", 1)
		self.sleep = int(records[1]) if records[1] != "NULL" else None
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTRACKDEF \"{self.trackdef}\"\n")
		w.write(f"\tINTERPOLATE {self.interpolate}\n")
		w.write(f"\tREVERSE {self.reverse}\n")
		w.write(f"\tSLEEP? {('NULL' if self.sleep is None else self.sleep)}\n")
		return ""

