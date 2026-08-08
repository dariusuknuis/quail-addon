# Generated from quail, DO NOT EDIT
import io
from .parse import property

class emitterdef:
	@staticmethod
	def definition():
		return "EMITTERDEF"

	tag:str
	name:str
	texture:str
	relativetobone:int
	noocclusion:int
	additiveblending:int
	scalewithactor:int
	spriteorientation:int
	sticktoactor:int
	defaultlifespan:float
	particlelifespan:float
	particlesatcreation:int
	particlesatinterval:int
	intervalspersecond:float
	spawndelay:float
	fadeintime:float
	fadeouttime:float
	scaleintime:float
	scaleouttime:float
	reductiondistance:float
	maxalpha:float
	spawnshape:int
	shaperadius:float
	shaperadiusminor:float
	shapeheight:float
	shapeoffset:tuple[float, float, float]
	shapetilt:tuple[float, float]
	particlewidthmin:float
	particlezbias:float
	tintstart:tuple[int, int, int]
	tintend:tuple[int, int, int]
	speedmin:tuple[float, float, float]
	speedmax:tuple[float, float, float]
	acceleration:tuple[float, float, float]
	outwardspeedmin:float
	outwardspeedmax:float
	outwardspeedacceleration:float
	orbitalspeedmin:float
	orbitalspeedmax:float
	orbitalspeedacceleration:float
	scalargravity:float
	windspeed:float
	animationframes:int
	animationrate:float
	particlespinrate:float
	oldparticletype:int
	oldflags:int
	oldsize:int
	gravity:tuple[float, float, float]
	bbmin:tuple[float, float, float]
	bbmax:tuple[float, float, float]
	spawnscale:float
	alpha:float
	randomrotation:int
	particleorientation:int
	particleheightmin:float
	particleheightmax:float
	particlewidthmax:float
	particlespinratemax:float
	proportionalsizescaling:int
	heightsquashtime:float
	widthsquashtime:float
	allowcenterpassthrough:int
	scaleemitterwithactor:int

	def __init__(self):
		self.tag = ""
		self.name = "" #2
		self.texture = "" #2
		self.relativetobone = 0 #2
		self.noocclusion = 0 #2
		self.additiveblending = 0 #2
		self.scalewithactor = 0 #2
		self.spriteorientation = 0 #2
		self.sticktoactor = 0 #2
		self.defaultlifespan = 0.0 #2
		self.particlelifespan = 0.0 #2
		self.particlesatcreation = 0 #2
		self.particlesatinterval = 0 #2
		self.intervalspersecond = 0.0 #2
		self.spawndelay = 0.0 #2
		self.fadeintime = 0.0 #2
		self.fadeouttime = 0.0 #2
		self.scaleintime = 0.0 #2
		self.scaleouttime = 0.0 #2
		self.reductiondistance = 0.0 #2
		self.maxalpha = 0.0 #2
		self.spawnshape = 0 #2
		self.shaperadius = 0.0 #2
		self.shaperadiusminor = 0.0 #2
		self.shapeheight = 0.0 #2
		self.shapeoffset = (0.0, 0.0, 0.0) #2
		self.shapetilt = (0.0, 0.0) #2
		self.particlewidthmin = 0.0 #2
		self.particlezbias = 0.0 #2
		self.tintstart = (0, 0, 0) #2
		self.tintend = (0, 0, 0) #2
		self.speedmin = (0.0, 0.0, 0.0) #2
		self.speedmax = (0.0, 0.0, 0.0) #2
		self.acceleration = (0.0, 0.0, 0.0) #2
		self.outwardspeedmin = 0.0 #2
		self.outwardspeedmax = 0.0 #2
		self.outwardspeedacceleration = 0.0 #2
		self.orbitalspeedmin = 0.0 #2
		self.orbitalspeedmax = 0.0 #2
		self.orbitalspeedacceleration = 0.0 #2
		self.scalargravity = 0.0 #2
		self.windspeed = 0.0 #2
		self.animationframes = 0 #2
		self.animationrate = 0.0 #2
		self.particlespinrate = 0.0 #2
		self.oldparticletype = 0 #2
		self.oldflags = 0 #2
		self.oldsize = 0 #2
		self.gravity = (0.0, 0.0, 0.0) #2
		self.bbmin = (0.0, 0.0, 0.0) #2
		self.bbmax = (0.0, 0.0, 0.0) #2
		self.spawnscale = 0.0 #2
		self.alpha = 0.0 #2
		self.randomrotation = 0 #2
		self.particleorientation = 0 #2
		self.particleheightmin = 0.0 #2
		self.particleheightmax = 0.0 #2
		self.particlewidthmax = 0.0 #2
		self.particlespinratemax = 0.0 #2
		self.proportionalsizescaling = 0 #2
		self.heightsquashtime = 0.0 #2
		self.widthsquashtime = 0.0 #2
		self.allowcenterpassthrough = 0 #2
		self.scaleemitterwithactor = 0 #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NAME", 1)
		self.name = str(records[1])
		records = property(r, "TEXTURE", 1)
		self.texture = str(records[1])
		records = property(r, "RELATIVETOBONE", 1)
		self.relativetobone = int(records[1])
		records = property(r, "NOOCCLUSION", 1)
		self.noocclusion = int(records[1])
		records = property(r, "ADDITIVEBLENDING", 1)
		self.additiveblending = int(records[1])
		records = property(r, "SCALEWITHACTOR", 1)
		self.scalewithactor = int(records[1])
		records = property(r, "SPRITEORIENTATION", 1)
		self.spriteorientation = int(records[1])
		records = property(r, "STICKTOACTOR", 1)
		self.sticktoactor = int(records[1])
		records = property(r, "DEFAULTLIFESPAN", 1)
		self.defaultlifespan = float(records[1])
		records = property(r, "PARTICLELIFESPAN", 1)
		self.particlelifespan = float(records[1])
		records = property(r, "PARTICLESATCREATION", 1)
		self.particlesatcreation = int(records[1])
		records = property(r, "PARTICLESATINTERVAL", 1)
		self.particlesatinterval = int(records[1])
		records = property(r, "INTERVALSPERSECOND", 1)
		self.intervalspersecond = float(records[1])
		records = property(r, "SPAWNDELAY", 1)
		self.spawndelay = float(records[1])
		records = property(r, "FADEINTIME", 1)
		self.fadeintime = float(records[1])
		records = property(r, "FADEOUTTIME", 1)
		self.fadeouttime = float(records[1])
		records = property(r, "SCALEINTIME", 1)
		self.scaleintime = float(records[1])
		records = property(r, "SCALEOUTTIME", 1)
		self.scaleouttime = float(records[1])
		records = property(r, "REDUCTIONDISTANCE", 1)
		self.reductiondistance = float(records[1])
		records = property(r, "MAXALPHA", 1)
		self.maxalpha = float(records[1])
		records = property(r, "SPAWNSHAPE", 1)
		self.spawnshape = int(records[1])
		records = property(r, "SHAPERADIUS", 1)
		self.shaperadius = float(records[1])
		records = property(r, "SHAPERADIUSMINOR", 1)
		self.shaperadiusminor = float(records[1])
		records = property(r, "SHAPEHEIGHT", 1)
		self.shapeheight = float(records[1])
		records = property(r, "SHAPEOFFSET", 3)
		self.shapeoffset = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "SHAPETILT", 2)
		self.shapetilt = (float(records[1]), float(records[2]))
		records = property(r, "PARTICLEWIDTHMIN", 1)
		self.particlewidthmin = float(records[1])
		records = property(r, "PARTICLEZBIAS", 1)
		self.particlezbias = float(records[1])
		records = property(r, "TINTSTART", 3)
		self.tintstart = (int(records[1]), int(records[2]), int(records[3]))
		records = property(r, "TINTEND", 3)
		self.tintend = (int(records[1]), int(records[2]), int(records[3]))
		records = property(r, "SPEEDMIN", 3)
		self.speedmin = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "SPEEDMAX", 3)
		self.speedmax = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "ACCELERATION", 3)
		self.acceleration = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "OUTWARDSPEEDMIN", 1)
		self.outwardspeedmin = float(records[1])
		records = property(r, "OUTWARDSPEEDMAX", 1)
		self.outwardspeedmax = float(records[1])
		records = property(r, "OUTWARDSPEEDACCELERATION", 1)
		self.outwardspeedacceleration = float(records[1])
		records = property(r, "ORBITALSPEEDMIN", 1)
		self.orbitalspeedmin = float(records[1])
		records = property(r, "ORBITALSPEEDMAX", 1)
		self.orbitalspeedmax = float(records[1])
		records = property(r, "ORBITALSPEEDACCELERATION", 1)
		self.orbitalspeedacceleration = float(records[1])
		records = property(r, "SCALARGRAVITY", 1)
		self.scalargravity = float(records[1])
		records = property(r, "WINDSPEED", 1)
		self.windspeed = float(records[1])
		records = property(r, "ANIMATIONFRAMES", 1)
		self.animationframes = int(records[1])
		records = property(r, "ANIMATIONRATE", 1)
		self.animationrate = float(records[1])
		records = property(r, "PARTICLESPINRATE", 1)
		self.particlespinrate = float(records[1])
		records = property(r, "OLDPARTICLETYPE", 1)
		self.oldparticletype = int(records[1])
		records = property(r, "OLDFLAGS", 1)
		self.oldflags = int(records[1])
		records = property(r, "OLDSIZE", 1)
		self.oldsize = int(records[1])
		records = property(r, "GRAVITY", 3)
		self.gravity = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BBMIN", 3)
		self.bbmin = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BBMAX", 3)
		self.bbmax = (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "SPAWNSCALE", 1)
		self.spawnscale = float(records[1])
		records = property(r, "ALPHA", 1)
		self.alpha = float(records[1])
		records = property(r, "RANDOMROTATION", 1)
		self.randomrotation = int(records[1])
		records = property(r, "PARTICLEORIENTATION", 1)
		self.particleorientation = int(records[1])
		records = property(r, "PARTICLEHEIGHTMIN", 1)
		self.particleheightmin = float(records[1])
		records = property(r, "PARTICLEHEIGHTMAX", 1)
		self.particleheightmax = float(records[1])
		records = property(r, "PARTICLEWIDTHMAX", 1)
		self.particlewidthmax = float(records[1])
		records = property(r, "PARTICLESPINRATEMAX", 1)
		self.particlespinratemax = float(records[1])
		records = property(r, "PROPORTIONALSIZESCALING", 1)
		self.proportionalsizescaling = int(records[1])
		records = property(r, "HEIGHTSQUASHTIME", 1)
		self.heightsquashtime = float(records[1])
		records = property(r, "WIDTHSQUASHTIME", 1)
		self.widthsquashtime = float(records[1])
		records = property(r, "ALLOWCENTERPASSTHROUGH", 1)
		self.allowcenterpassthrough = int(records[1])
		records = property(r, "SCALEEMITTERWITHACTOR", 1)
		self.scaleemitterwithactor = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNAME \"{self.name}\"\n")
		w.write(f"\tTEXTURE \"{self.texture}\"\n")
		w.write(f"\tRELATIVETOBONE {self.relativetobone}\n")
		w.write(f"\tNOOCCLUSION {self.noocclusion}\n")
		w.write(f"\tADDITIVEBLENDING {self.additiveblending}\n")
		w.write(f"\tSCALEWITHACTOR {self.scalewithactor}\n")
		w.write(f"\tSPRITEORIENTATION {self.spriteorientation}\n")
		w.write(f"\tSTICKTOACTOR {self.sticktoactor}\n")
		w.write(f"\tDEFAULTLIFESPAN {format(self.defaultlifespan, '.8e')}\n")
		w.write(f"\tPARTICLELIFESPAN {format(self.particlelifespan, '.8e')}\n")
		w.write(f"\tPARTICLESATCREATION {self.particlesatcreation}\n")
		w.write(f"\tPARTICLESATINTERVAL {self.particlesatinterval}\n")
		w.write(f"\tINTERVALSPERSECOND {format(self.intervalspersecond, '.8e')}\n")
		w.write(f"\tSPAWNDELAY {format(self.spawndelay, '.8e')}\n")
		w.write(f"\tFADEINTIME {format(self.fadeintime, '.8e')}\n")
		w.write(f"\tFADEOUTTIME {format(self.fadeouttime, '.8e')}\n")
		w.write(f"\tSCALEINTIME {format(self.scaleintime, '.8e')}\n")
		w.write(f"\tSCALEOUTTIME {format(self.scaleouttime, '.8e')}\n")
		w.write(f"\tREDUCTIONDISTANCE {format(self.reductiondistance, '.8e')}\n")
		w.write(f"\tMAXALPHA {format(self.maxalpha, '.8e')}\n")
		w.write(f"\tSPAWNSHAPE {self.spawnshape}\n")
		w.write(f"\tSHAPERADIUS {format(self.shaperadius, '.8e')}\n")
		w.write(f"\tSHAPERADIUSMINOR {format(self.shaperadiusminor, '.8e')}\n")
		w.write(f"\tSHAPEHEIGHT {format(self.shapeheight, '.8e')}\n")
		w.write(f"\tSHAPEOFFSET {format(self.shapeoffset[0], '.8e')} {format(self.shapeoffset[1], '.8e')} {format(self.shapeoffset[2], '.8e')}\n")
		w.write(f"\tSHAPETILT {format(self.shapetilt[0], '.8e')} {format(self.shapetilt[1], '.8e')}\n")
		w.write(f"\tPARTICLEWIDTHMIN {format(self.particlewidthmin, '.8e')}\n")
		w.write(f"\tPARTICLEZBIAS {format(self.particlezbias, '.8e')}\n")
		w.write(f"\tTINTSTART {self.tintstart[0]} {self.tintstart[1]} {self.tintstart[2]}\n")
		w.write(f"\tTINTEND {self.tintend[0]} {self.tintend[1]} {self.tintend[2]}\n")
		w.write(f"\tSPEEDMIN {format(self.speedmin[0], '.8e')} {format(self.speedmin[1], '.8e')} {format(self.speedmin[2], '.8e')}\n")
		w.write(f"\tSPEEDMAX {format(self.speedmax[0], '.8e')} {format(self.speedmax[1], '.8e')} {format(self.speedmax[2], '.8e')}\n")
		w.write(f"\tACCELERATION {format(self.acceleration[0], '.8e')} {format(self.acceleration[1], '.8e')} {format(self.acceleration[2], '.8e')}\n")
		w.write(f"\tOUTWARDSPEEDMIN {format(self.outwardspeedmin, '.8e')}\n")
		w.write(f"\tOUTWARDSPEEDMAX {format(self.outwardspeedmax, '.8e')}\n")
		w.write(f"\tOUTWARDSPEEDACCELERATION {format(self.outwardspeedacceleration, '.8e')}\n")
		w.write(f"\tORBITALSPEEDMIN {format(self.orbitalspeedmin, '.8e')}\n")
		w.write(f"\tORBITALSPEEDMAX {format(self.orbitalspeedmax, '.8e')}\n")
		w.write(f"\tORBITALSPEEDACCELERATION {format(self.orbitalspeedacceleration, '.8e')}\n")
		w.write(f"\tSCALARGRAVITY {format(self.scalargravity, '.8e')}\n")
		w.write(f"\tWINDSPEED {format(self.windspeed, '.8e')}\n")
		w.write(f"\tANIMATIONFRAMES {self.animationframes}\n")
		w.write(f"\tANIMATIONRATE {format(self.animationrate, '.8e')}\n")
		w.write(f"\tPARTICLESPINRATE {format(self.particlespinrate, '.8e')}\n")
		w.write(f"\tOLDPARTICLETYPE {self.oldparticletype}\n")
		w.write(f"\tOLDFLAGS {self.oldflags}\n")
		w.write(f"\tOLDSIZE {self.oldsize}\n")
		w.write(f"\tGRAVITY {format(self.gravity[0], '.8e')} {format(self.gravity[1], '.8e')} {format(self.gravity[2], '.8e')}\n")
		w.write(f"\tBBMIN {format(self.bbmin[0], '.8e')} {format(self.bbmin[1], '.8e')} {format(self.bbmin[2], '.8e')}\n")
		w.write(f"\tBBMAX {format(self.bbmax[0], '.8e')} {format(self.bbmax[1], '.8e')} {format(self.bbmax[2], '.8e')}\n")
		w.write(f"\tSPAWNSCALE {format(self.spawnscale, '.8e')}\n")
		w.write(f"\tALPHA {format(self.alpha, '.8e')}\n")
		w.write(f"\tRANDOMROTATION {self.randomrotation}\n")
		w.write(f"\tPARTICLEORIENTATION {self.particleorientation}\n")
		w.write(f"\tPARTICLEHEIGHTMIN {format(self.particleheightmin, '.8e')}\n")
		w.write(f"\tPARTICLEHEIGHTMAX {format(self.particleheightmax, '.8e')}\n")
		w.write(f"\tPARTICLEWIDTHMAX {format(self.particlewidthmax, '.8e')}\n")
		w.write(f"\tPARTICLESPINRATEMAX {format(self.particlespinratemax, '.8e')}\n")
		w.write(f"\tPROPORTIONALSIZESCALING {self.proportionalsizescaling}\n")
		w.write(f"\tHEIGHTSQUASHTIME {format(self.heightsquashtime, '.8e')}\n")
		w.write(f"\tWIDTHSQUASHTIME {format(self.widthsquashtime, '.8e')}\n")
		w.write(f"\tALLOWCENTERPASSTHROUGH {self.allowcenterpassthrough}\n")
		w.write(f"\tSCALEEMITTERWITHACTOR {self.scaleemitterwithactor}\n")
		return ""

