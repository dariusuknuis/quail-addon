# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class blitspritedef:
	@staticmethod
	def definition():
		return "BLITSPRITEDEF"

	tag:str
	sprite:str # Sprite tag
	rendermethod:str # Method for rendering
	transparent:int # Is Transparent

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = parse.property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		records = parse.property(r, "TRANSPARENT", 1)
		self.transparent = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tTRANSPARENT \"{self.transparent}\"\n")

