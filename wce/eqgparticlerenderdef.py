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
		particlepoint:str
		particletype:int
		animnumber:int
		animvariation:int
		randomanim:int
		starttime:int
		lifespan:int
		ground:int
		playwithmat:int
		sporadic:int
		coldemitterid:int

		def __init__(self):
			self.render = 0 #3
			self.particlepoint = "" #3
			self.particletype = 0 #3
			self.animnumber = 0 #3
			self.animvariation = 0 #3
			self.randomanim = 0 #3
			self.starttime = 0 #3
			self.lifespan = 0 #3
			self.ground = 0 #3
			self.playwithmat = 0 #3
			self.sporadic = 0 #3
			self.coldemitterid = 0 #3

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
			records = property(r, "PARTICLEPOINT", 1)
			renderi.particlepoint = str(records[1])
			records = property(r, "PARTICLETYPE", 1)
			renderi.particletype = int(records[1])
			records = property(r, "ANIMNUMBER", 1)
			renderi.animnumber = int(records[1])
			records = property(r, "ANIMVARIATION", 1)
			renderi.animvariation = int(records[1])
			records = property(r, "RANDOMANIM", 1)
			renderi.randomanim = int(records[1])
			records = property(r, "STARTTIME", 1)
			renderi.starttime = int(records[1])
			records = property(r, "LIFESPAN", 1)
			renderi.lifespan = int(records[1])
			records = property(r, "GROUND", 1)
			renderi.ground = int(records[1])
			records = property(r, "PLAYWITHMAT", 1)
			renderi.playwithmat = int(records[1])
			records = property(r, "SPORADIC", 1)
			renderi.sporadic = int(records[1])
			records = property(r, "COLDEMITTERID", 1)
			renderi.coldemitterid = int(records[1])
			self.renders.append(renderi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION {self.version}\n")
		w.write(f"\tNUMRENDERS {len(self.renders)}\n")
		for renderi in self.renders:
			w.write(f"\t\tRENDER {renderi.render}\n")
			w.write(f"\t\tPARTICLEPOINT \"{renderi.particlepoint}\"\n")
			w.write(f"\t\tPARTICLETYPE {renderi.particletype}\n")
			w.write(f"\t\tANIMNUMBER {renderi.animnumber}\n")
			w.write(f"\t\tANIMVARIATION {renderi.animvariation}\n")
			w.write(f"\t\tRANDOMANIM {renderi.randomanim}\n")
			w.write(f"\t\tSTARTTIME {renderi.starttime}\n")
			w.write(f"\t\tLIFESPAN {renderi.lifespan}\n")
			w.write(f"\t\tGROUND {renderi.ground}\n")
			w.write(f"\t\tPLAYWITHMAT {renderi.playwithmat}\n")
			w.write(f"\t\tSPORADIC {renderi.sporadic}\n")
			w.write(f"\t\tCOLDEMITTERID {renderi.coldemitterid}\n")
		return ""

