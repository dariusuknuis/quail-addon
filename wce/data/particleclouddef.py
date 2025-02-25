# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

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
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "BLITTAG", 1)
		self.blittag = str(records[1])
		records = parse.property(r, "PARTICLETYPE", 1)
		self.particletype = int(records[1])
		records = parse.property(r, "MOVEMENT", 1)
		self.movement = str(records[1])
		records = parse.property(r, "HIGHOPACITY", 1)
		self.highopacity = int(records[1])
		records = parse.property(r, "FOLLOWITEM", 1)
		self.followitem = int(records[1])
		records = parse.property(r, "SIZE", 1)
		self.size = int(records[1])
		records = parse.property(r, "GRAVITYMULTIPLIER", 1)
		self.gravitymultiplier = float(records[1])
		records = parse.property(r, "GRAVITY", 3)
		self.gravity = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "DURATION", 1)
		self.duration = int(records[1])
		records = parse.property(r, "SPAWNRADIUS", 1)
		self.spawnradius = float(records[1])
		records = parse.property(r, "SPAWNANGLE", 1)
		self.spawnangle = float(records[1])
		records = parse.property(r, "LIFESPAN", 1)
		self.lifespan = int(records[1])
		records = parse.property(r, "SPAWNVELOCITYMULTIPLIER", 1)
		self.spawnvelocitymultiplier = float(records[1])
		records = parse.property(r, "SPAWNVELOCITY", 3)
		self.spawnvelocity = float(records[1]), float(records[2]), float(records[3])
		records = parse.property(r, "SPAWNRATE", 1)
		self.spawnrate = int(records[1])
		records = parse.property(r, "SPAWNSCALE", 1)
		self.spawnscale = float(records[1])
		records = parse.property(r, "TINT", 4)
		self.tint = int(records[1]), int(records[2]), int(records[3]), int(records[4])
		records = parse.property(r, "SPAWNBOXMIN?", 3)
		self.spawnboxmin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "SPAWNBOXMAX?", 3)
		self.spawnboxmax = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "BOXMIN?", 3)
		self.boxmin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "BOXMAX?", 3)
		self.boxmax = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "HEXEIGHTYFLAG", 1)
		self.hexeightyflag = int(records[1])
		records = parse.property(r, "HEXONEHUNDREDFLAG", 1)
		self.hexonehundredflag = int(records[1])
		records = parse.property(r, "HEXFOURHUNDREDFLAG", 1)
		self.hexfourhundredflag = int(records[1])
		records = parse.property(r, "HEXFOURTHOUSANDFLAG", 1)
		self.hexfourthousandflag = int(records[1])
		records = parse.property(r, "HEXEIGHTTHOUSANDFLAG", 1)
		self.hexeightthousandflag = int(records[1])
		records = parse.property(r, "HEXTENTHOUSANDFLAG", 1)
		self.hextenthousandflag = int(records[1])
		records = parse.property(r, "HEXTWENTYTHOUSANDFLAG", 1)
		self.hextwentythousandflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"TAGINDEX \"{self.tagindex}\"\n")
		w.write(f"BLITTAG \"{self.blittag}\"\n")
		w.write(f"PARTICLETYPE \"{self.particletype}\"\n")
		w.write(f"MOVEMENT \"{self.movement}\"\n")
		w.write(f"HIGHOPACITY \"{self.highopacity}\"\n")
		w.write(f"FOLLOWITEM \"{self.followitem}\"\n")
		w.write(f"SIZE \"{self.size}\"\n")
		w.write(f"GRAVITYMULTIPLIER \"{self.gravitymultiplier}\"\n")
		w.write(f"GRAVITY \"{self.gravity}\"\n")
		w.write(f"DURATION \"{self.duration}\"\n")
		w.write(f"SPAWNRADIUS \"{self.spawnradius}\"\n")
		w.write(f"SPAWNANGLE \"{self.spawnangle}\"\n")
		w.write(f"LIFESPAN \"{self.lifespan}\"\n")
		w.write(f"SPAWNVELOCITYMULTIPLIER \"{self.spawnvelocitymultiplier}\"\n")
		w.write(f"SPAWNVELOCITY \"{self.spawnvelocity}\"\n")
		w.write(f"SPAWNRATE \"{self.spawnrate}\"\n")
		w.write(f"SPAWNSCALE \"{self.spawnscale}\"\n")
		w.write(f"TINT \"{self.tint}\"\n")
		w.write(f"SPAWNBOXMIN? \"{self.spawnboxmin}\"\n")
		w.write(f"SPAWNBOXMAX? \"{self.spawnboxmax}\"\n")
		w.write(f"BOXMIN? \"{self.boxmin}\"\n")
		w.write(f"BOXMAX? \"{self.boxmax}\"\n")
		w.write(f"HEXEIGHTYFLAG \"{self.hexeightyflag}\"\n")
		w.write(f"HEXONEHUNDREDFLAG \"{self.hexonehundredflag}\"\n")
		w.write(f"HEXFOURHUNDREDFLAG \"{self.hexfourhundredflag}\"\n")
		w.write(f"HEXFOURTHOUSANDFLAG \"{self.hexfourthousandflag}\"\n")
		w.write(f"HEXEIGHTTHOUSANDFLAG \"{self.hexeightthousandflag}\"\n")
		w.write(f"HEXTENTHOUSANDFLAG \"{self.hextenthousandflag}\"\n")
		w.write(f"HEXTWENTYTHOUSANDFLAG \"{self.hextwentythousandflag}\"\n")

