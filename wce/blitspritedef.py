# Generated from quail, DO NOT EDIT
import io
from .parse import property

class blitspritedef:
	@staticmethod
	def definition():
		return "BLITSPRITEDEF"

	tag:str
	sprite:str
	rendermethod:str
	transparent:int

	def __init__(self):
		self.tag = ""
		self.sprite = "" #2
		self.rendermethod = "" #2
		self.transparent = 0 #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		records = property(r, "TRANSPARENT", 1)
		self.transparent = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tTRANSPARENT \"{self.transparent}\"\n")
		return ""

