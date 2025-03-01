# Generated from quail, DO NOT EDIT
import io
from .parse import property

class particleclouddef:
	@staticmethod
	def definition():
		return "PARTICLECLOUDDEF"

	tag:str
	tagindex:int
	blittag:str
	particletype:int
	movement:str
	highopacity:int
	followitem:int
	size:int
	gravitymultiplier:float
	gravity:tuple[float, float, float]
	duration:int
	spawnradius:float
	spawnangle:float
	lifespan:int
	spawnvelocitymultiplier:float
	spawnvelocity:tuple[float, float, float]
	spawnrate:int
	spawnscale:float
	tint:tuple[int, int, int, int]
	spawnboxmin:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	spawnboxmax:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boxmin:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boxmax:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	hexeightyflag:int
	hexonehundredflag:int
	hexfourhundredflag:int
	hexfourthousandflag:int
	hexeightthousandflag:int
	hextenthousandflag:int
	hextwentythousandflag:int

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "BLITTAG", 1)
		self.blittag = str(records[1])
		records = property(r, "PARTICLETYPE", 1)
		self.particletype = int(records[1])
		records = property(r, "MOVEMENT", 1)
		self.movement = str(records[1])
		records = property(r, "HIGHOPACITY", 1)
		self.highopacity = int(records[1])
		records = property(r, "FOLLOWITEM", 1)
		self.followitem = int(records[1])
		records = property(r, "SIZE", 1)
		self.size = int(records[1])
		records = property(r, "GRAVITYMULTIPLIER", 1)
		self.gravitymultiplier = float(records[1])
		records = property(r, "GRAVITY", 3)
		self.gravity = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "DURATION", 1)
		self.duration = int(records[1])
		records = property(r, "SPAWNRADIUS", 1)
		self.spawnradius = float(records[1])
		records = property(r, "SPAWNANGLE", 1)
		self.spawnangle = float(records[1])
		records = property(r, "LIFESPAN", 1)
		self.lifespan = int(records[1])
		records = property(r, "SPAWNVELOCITYMULTIPLIER", 1)
		self.spawnvelocitymultiplier = float(records[1])
		records = property(r, "SPAWNVELOCITY", 3)
		self.spawnvelocity = float(records[1]), float(records[2]), float(records[3])
		records = property(r, "SPAWNRATE", 1)
		self.spawnrate = int(records[1])
		records = property(r, "SPAWNSCALE", 1)
		self.spawnscale = float(records[1])
		records = property(r, "TINT", 4)
		self.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
		records = property(r, "SPAWNBOXMIN?", 3)
		self.spawnboxmin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "SPAWNBOXMAX?", 3)
		self.spawnboxmax = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "BOXMIN?", 3)
		self.boxmin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "BOXMAX?", 3)
		self.boxmax = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "HEXEIGHTYFLAG", 1)
		self.hexeightyflag = int(records[1])
		records = property(r, "HEXONEHUNDREDFLAG", 1)
		self.hexonehundredflag = int(records[1])
		records = property(r, "HEXFOURHUNDREDFLAG", 1)
		self.hexfourhundredflag = int(records[1])
		records = property(r, "HEXFOURTHOUSANDFLAG", 1)
		self.hexfourthousandflag = int(records[1])
		records = property(r, "HEXEIGHTTHOUSANDFLAG", 1)
		self.hexeightthousandflag = int(records[1])
		records = property(r, "HEXTENTHOUSANDFLAG", 1)
		self.hextenthousandflag = int(records[1])
		records = property(r, "HEXTWENTYTHOUSANDFLAG", 1)
		self.hextwentythousandflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tBLITTAG \"{self.blittag}\"\n")
		w.write(f"\tPARTICLETYPE \"{self.particletype}\"\n")
		w.write(f"\tMOVEMENT \"{self.movement}\"\n")
		w.write(f"\tHIGHOPACITY \"{self.highopacity}\"\n")
		w.write(f"\tFOLLOWITEM \"{self.followitem}\"\n")
		w.write(f"\tSIZE \"{self.size}\"\n")
		w.write(f"\tGRAVITYMULTIPLIER \"{self.gravitymultiplier}\"\n")
		w.write(f"\tGRAVITY \"{self.gravity}\"\n")
		w.write(f"\tDURATION \"{self.duration}\"\n")
		w.write(f"\tSPAWNRADIUS \"{self.spawnradius}\"\n")
		w.write(f"\tSPAWNANGLE \"{self.spawnangle}\"\n")
		w.write(f"\tLIFESPAN \"{self.lifespan}\"\n")
		w.write(f"\tSPAWNVELOCITYMULTIPLIER \"{self.spawnvelocitymultiplier}\"\n")
		w.write(f"\tSPAWNVELOCITY \"{self.spawnvelocity}\"\n")
		w.write(f"\tSPAWNRATE \"{self.spawnrate}\"\n")
		w.write(f"\tSPAWNSCALE \"{self.spawnscale}\"\n")
		w.write(f"\tTINT \"{self.tint}\"\n")
		w.write(f"\tSPAWNBOXMIN? \"{self.spawnboxmin}\"\n")
		w.write(f"\tSPAWNBOXMAX? \"{self.spawnboxmax}\"\n")
		w.write(f"\tBOXMIN? \"{self.boxmin}\"\n")
		w.write(f"\tBOXMAX? \"{self.boxmax}\"\n")
		w.write(f"\tHEXEIGHTYFLAG \"{self.hexeightyflag}\"\n")
		w.write(f"\tHEXONEHUNDREDFLAG \"{self.hexonehundredflag}\"\n")
		w.write(f"\tHEXFOURHUNDREDFLAG \"{self.hexfourhundredflag}\"\n")
		w.write(f"\tHEXFOURTHOUSANDFLAG \"{self.hexfourthousandflag}\"\n")
		w.write(f"\tHEXEIGHTTHOUSANDFLAG \"{self.hexeightthousandflag}\"\n")
		w.write(f"\tHEXTENTHOUSANDFLAG \"{self.hextenthousandflag}\"\n")
		w.write(f"\tHEXTWENTYTHOUSANDFLAG \"{self.hextwentythousandflag}\"\n")

