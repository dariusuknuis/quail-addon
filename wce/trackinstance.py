# Generated from quail, DO NOT EDIT
import io
from .parse import property

class trackinstance:
	@staticmethod
	def definition():
		return "TRACKINSTANCE"

	tag:str
	tagindex:int
	sprite:str
	spriteindex:int
	interpolate:int # deprecated, ignored in RoF2
	reverse:int # deprecated, ignored in RoF2
	sleep:tuple[int, None]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "SPRITEINDEX", 1)
		self.spriteindex = int(records[1])
		records = property(r, "INTERPOLATE", 1)
		self.interpolate = int(records[1])
		records = property(r, "REVERSE", 1)
		self.reverse = int(records[1])
		records = property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tSPRITEINDEX \"{self.spriteindex}\"\n")
		w.write(f"\tINTERPOLATE \"{self.interpolate}\"\n")
		w.write(f"\tREVERSE \"{self.reverse}\"\n")
		w.write(f"\tSLEEP? \"{self.sleep}\"\n")

