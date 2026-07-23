# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqganldef:
	@staticmethod
	def definition():
		return "EQGANLDEF"

	tag:str
	version:int
	defaultanimation:str

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.defaultanimation = "" #2
		self.animations = []

	class animation:
		animation:str

		def __init__(self):
			self.animation = "" #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMANIMATIONS", 1)
		numanimations = int(records[1])

		self.animations = []
		for i in range(numanimations):
			animationi = type(self).animation()
			records = property(r, "ANIMATION", 1)
			animationi.animation = str(records[1])
			self.animations.append(animationi)
		records = property(r, "DEFAULTANIMATION", 1)
		self.defaultanimation = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMANIMATIONS {len(self.animations)}\n")
		for animationi in self.animations:
			w.write(f"\t\tANIMATION \"{animationi.animation}\"\n")
		w.write(f"\tDEFAULTANIMATION \"{self.defaultanimation}\"\n")
		return ""

