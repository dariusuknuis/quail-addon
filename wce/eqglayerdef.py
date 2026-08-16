# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqglayerdef:
	@staticmethod
	def definition():
		return "EQGLAYERDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.layers = []

	class layer:
		material:str
		texture0:str
		texture1:str
		texture2:str
		texture3:str
		texture4:str
		shininess:float
		rendertype:float

		def __init__(self):
			self.material = "" #3
			self.texture0 = "" #3
			self.texture1 = "" #3
			self.texture2 = "" #3
			self.texture3 = "" #3
			self.texture4 = "" #3
			self.shininess = 0.0 #3
			self.rendertype = 0.0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMLAYERS", 1)
		numlayers = int(records[1])

		self.layers = []
		for i in range(numlayers):
			layeri = type(self).layer()
			property(r, "LAYER", 0)

			records = property(r, "MATERIAL", 1)
			layeri.material = str(records[1])
			records = property(r, "TEXTURE0", 1)
			layeri.texture0 = str(records[1])
			records = property(r, "TEXTURE1", 1)
			layeri.texture1 = str(records[1])
			records = property(r, "TEXTURE2", 1)
			layeri.texture2 = str(records[1])
			records = property(r, "TEXTURE3", 1)
			layeri.texture3 = str(records[1])
			records = property(r, "TEXTURE4", 1)
			layeri.texture4 = str(records[1])
			records = property(r, "SHININESS", 1)
			layeri.shininess = float(records[1])
			records = property(r, "RENDERTYPE", 1)
			layeri.rendertype = float(records[1])
			self.layers.append(layeri)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMLAYERS {len(self.layers)}\n")
		for layeri in self.layers:
			w.write(f"\t\tLAYER\n")
			w.write(f"\t\tMATERIAL \"{layeri.material}\"\n")
			w.write(f"\t\tTEXTURE0 \"{layeri.texture0}\"\n")
			w.write(f"\t\tTEXTURE1 \"{layeri.texture1}\"\n")
			w.write(f"\t\tTEXTURE2 \"{layeri.texture2}\"\n")
			w.write(f"\t\tTEXTURE3 \"{layeri.texture3}\"\n")
			w.write(f"\t\tTEXTURE4 \"{layeri.texture4}\"\n")
			w.write(f"\t\tSHININESS {format(layeri.shininess, '.8e')}\n")
			w.write(f"\t\tRENDERTYPE {format(layeri.rendertype, '.8e')}\n")
		return ""

