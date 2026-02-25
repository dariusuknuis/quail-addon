# Generated from quail, DO NOT EDIT
import io
from .parse import property

class eqgparticlerenderdef:
	@staticmethod
	def definition():
		return "EQGPARTICLERENDERDEF"

	tag:str
	version:int

	def __init__(self):
		self.tag = ""
		self.version = 0 #2
		self.renders = []

	class render:
		render:int
		id2:int
		particlepoint:str
		particlesuffix:str
		unknowna1:int
		unknowna2:int
		unknowna3:int
		unknowna4:int
		unknowna5:int
		duration:int
		unknownb:int
		unknownffffffff:int
		unknownc:int

		def __init__(self):
			self.render = 0 #3
			self.id2 = 0 #3
			self.particlepoint = "" #3
			self.particlesuffix = "" #3
			self.unknowna1 = 0 #3
			self.unknowna2 = 0 #3
			self.unknowna3 = 0 #3
			self.unknowna4 = 0 #3
			self.unknowna5 = 0 #3
			self.duration = 0 #3
			self.unknownb = 0 #3
			self.unknownffffffff = 0 #3
			self.unknownc = 0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "VERSION", 1)
		self.version = int(records[1])
		records = property(r, "NUMRENDERS", 1)
		numrenders = int(records[1])

		self.renders = []
		for i in range(numrenders):
			renderi = type(self).render()
			records = property(r, "RENDER", 1)
			renderi.render = int(records[1])
			records = property(r, "ID2", 1)
			renderi.id2 = int(records[1])
			records = property(r, "PARTICLEPOINT", 1)
			renderi.particlepoint = str(records[1])
			records = property(r, "PARTICLESUFFIX", 1)
			renderi.particlesuffix = str(records[1])
			records = property(r, "UNKNOWNA1", 1)
			renderi.unknowna1 = int(records[1])
			records = property(r, "UNKNOWNA2", 1)
			renderi.unknowna2 = int(records[1])
			records = property(r, "UNKNOWNA3", 1)
			renderi.unknowna3 = int(records[1])
			records = property(r, "UNKNOWNA4", 1)
			renderi.unknowna4 = int(records[1])
			records = property(r, "UNKNOWNA5", 1)
			renderi.unknowna5 = int(records[1])
			records = property(r, "DURATION", 1)
			renderi.duration = int(records[1])
			records = property(r, "UNKNOWNB", 1)
			renderi.unknownb = int(records[1])
			records = property(r, "UNKNOWNFFFFFFFF", 1)
			renderi.unknownffffffff = int(records[1])
			records = property(r, "UNKNOWNC", 1)
			renderi.unknownc = int(records[1])
			self.renders.append(renderi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMRENDERS \"{len(self.renders)}\"\n")
		for renderi in self.renders:
			w.write(f"\t\tRENDER \"{renderi.render}\"\n")
			w.write(f"\t\tID2 \"{renderi.id2}\"\n")
			w.write(f"\t\tPARTICLEPOINT \"{renderi.particlepoint}\"\n")
			w.write(f"\t\tPARTICLESUFFIX \"{renderi.particlesuffix}\"\n")
			w.write(f"\t\tUNKNOWNA1 \"{renderi.unknowna1}\"\n")
			w.write(f"\t\tUNKNOWNA2 \"{renderi.unknowna2}\"\n")
			w.write(f"\t\tUNKNOWNA3 \"{renderi.unknowna3}\"\n")
			w.write(f"\t\tUNKNOWNA4 \"{renderi.unknowna4}\"\n")
			w.write(f"\t\tUNKNOWNA5 \"{renderi.unknowna5}\"\n")
			w.write(f"\t\tDURATION \"{renderi.duration}\"\n")
			w.write(f"\t\tUNKNOWNB \"{renderi.unknownb}\"\n")
			w.write(f"\t\tUNKNOWNFFFFFFFF \"{renderi.unknownffffffff}\"\n")
			w.write(f"\t\tUNKNOWNC \"{renderi.unknownc}\"\n")
		return ""

