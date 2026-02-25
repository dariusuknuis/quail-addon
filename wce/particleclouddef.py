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
	size:int
	gravity:float
	spawnnormal:tuple[float, float, float]
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
	usesprite:int
	free:int
	collision:int
	respawn:int
	viewrelx:int
	viewrely:int
	viewrelz:int
	viewwarp:int
	brownian:int
	fade:int
	boundingbox:int
	updatebbox:int
	pointgravity:int
	gravityflag:int
	freedef:int
	objectrelative:int
	parentobjrelative:int
	spawnscalerelative:int
	hidewithspawnobject:int

	def __init__(self):
		self.tag = ""
		self.tagindex = 0 #2
		self.blittag = "" #2
		self.particletype = 0 #2
		self.movement = "" #2
		self.size = 0 #2
		self.gravity = 0.0 #2
		self.spawnnormal = tuple[float, float, float] #2
		self.duration = 0 #2
		self.spawnradius = 0.0 #2
		self.spawnangle = 0.0 #2
		self.lifespan = 0 #2
		self.spawnvelocitymultiplier = 0.0 #2
		self.spawnvelocity = tuple[float, float, float] #2
		self.spawnrate = 0 #2
		self.spawnscale = 0.0 #2
		self.tint = tuple[int, int, int, int] #2
		self.spawnboxmin = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.spawnboxmax = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.boxmin = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.boxmax = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.usesprite = 0 #2
		self.free = 0 #2
		self.collision = 0 #2
		self.respawn = 0 #2
		self.viewrelx = 0 #2
		self.viewrely = 0 #2
		self.viewrelz = 0 #2
		self.viewwarp = 0 #2
		self.brownian = 0 #2
		self.fade = 0 #2
		self.boundingbox = 0 #2
		self.updatebbox = 0 #2
		self.pointgravity = 0 #2
		self.gravityflag = 0 #2
		self.freedef = 0 #2
		self.objectrelative = 0 #2
		self.parentobjrelative = 0 #2
		self.spawnscalerelative = 0 #2
		self.hidewithspawnobject = 0 #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "BLITTAG", 1)
		self.blittag = str(records[1])
		records = property(r, "PARTICLETYPE", 1)
		self.particletype = int(records[1])
		records = property(r, "MOVEMENT", 1)
		self.movement = str(records[1])
		records = property(r, "SIZE", 1)
		self.size = int(records[1])
		records = property(r, "GRAVITY", 1)
		self.gravity = float(records[1])
		records = property(r, "SPAWNNORMAL", 3)
		self.spawnnormal = float(records[1]), float(records[2]), float(records[3])
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
		records = property(r, "USESPRITE", 1)
		self.usesprite = int(records[1])
		records = property(r, "FREE", 1)
		self.free = int(records[1])
		records = property(r, "COLLISION", 1)
		self.collision = int(records[1])
		records = property(r, "RESPAWN", 1)
		self.respawn = int(records[1])
		records = property(r, "VIEWRELX", 1)
		self.viewrelx = int(records[1])
		records = property(r, "VIEWRELY", 1)
		self.viewrely = int(records[1])
		records = property(r, "VIEWRELZ", 1)
		self.viewrelz = int(records[1])
		records = property(r, "VIEWWARP", 1)
		self.viewwarp = int(records[1])
		records = property(r, "BROWNIAN", 1)
		self.brownian = int(records[1])
		records = property(r, "FADE", 1)
		self.fade = int(records[1])
		records = property(r, "BOUNDINGBOX", 1)
		self.boundingbox = int(records[1])
		records = property(r, "UPDATEBBOX", 1)
		self.updatebbox = int(records[1])
		records = property(r, "POINTGRAVITY", 1)
		self.pointgravity = int(records[1])
		records = property(r, "GRAVITYFLAG", 1)
		self.gravityflag = int(records[1])
		records = property(r, "FREEDEF", 1)
		self.freedef = int(records[1])
		records = property(r, "OBJECTRELATIVE", 1)
		self.objectrelative = int(records[1])
		records = property(r, "PARENTOBJRELATIVE", 1)
		self.parentobjrelative = int(records[1])
		records = property(r, "SPAWNSCALERELATIVE", 1)
		self.spawnscalerelative = int(records[1])
		records = property(r, "HIDEWITHSPAWNOBJECT", 1)
		self.hidewithspawnobject = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tBLITTAG \"{self.blittag}\"\n")
		w.write(f"\tPARTICLETYPE \"{self.particletype}\"\n")
		w.write(f"\tMOVEMENT \"{self.movement}\"\n")
		w.write(f"\tSIZE \"{self.size}\"\n")
		w.write(f"\tGRAVITY \"{self.gravity}\"\n")
		w.write(f"\tSPAWNNORMAL \"{self.spawnnormal}\"\n")
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
		w.write(f"\tUSESPRITE \"{self.usesprite}\"\n")
		w.write(f"\tFREE \"{self.free}\"\n")
		w.write(f"\tCOLLISION \"{self.collision}\"\n")
		w.write(f"\tRESPAWN \"{self.respawn}\"\n")
		w.write(f"\tVIEWRELX \"{self.viewrelx}\"\n")
		w.write(f"\tVIEWRELY \"{self.viewrely}\"\n")
		w.write(f"\tVIEWRELZ \"{self.viewrelz}\"\n")
		w.write(f"\tVIEWWARP \"{self.viewwarp}\"\n")
		w.write(f"\tBROWNIAN \"{self.brownian}\"\n")
		w.write(f"\tFADE \"{self.fade}\"\n")
		w.write(f"\tBOUNDINGBOX \"{self.boundingbox}\"\n")
		w.write(f"\tUPDATEBBOX \"{self.updatebbox}\"\n")
		w.write(f"\tPOINTGRAVITY \"{self.pointgravity}\"\n")
		w.write(f"\tGRAVITYFLAG \"{self.gravityflag}\"\n")
		w.write(f"\tFREEDEF \"{self.freedef}\"\n")
		w.write(f"\tOBJECTRELATIVE \"{self.objectrelative}\"\n")
		w.write(f"\tPARENTOBJRELATIVE \"{self.parentobjrelative}\"\n")
		w.write(f"\tSPAWNSCALERELATIVE \"{self.spawnscalerelative}\"\n")
		w.write(f"\tHIDEWITHSPAWNOBJECT \"{self.hidewithspawnobject}\"\n")
		return ""

