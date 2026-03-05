# Generated from quail, DO NOT EDIT
import io
from .parse import property

class actorinst:
	@staticmethod
	def definition():
		return "ACTORINST"

	tag:str
	sprite:str
	currentaction:tuple[str, None]
	location:tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None]]
	boundingradius:tuple[float, None]
	scalefactor:tuple[float, None]
	sound:tuple[str, None]
	active:tuple[int, None]
	spritevolumeonly:int
	dmrgbtrack:tuple[str, None]
	sphere:str
	sphereradius:float
	useboundingbox:int
	userdata:str

	def __init__(self):
		self.tag = ""
		self.sprite = "" #2
		self.currentaction = tuple[str, None] #2
		self.location = tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.boundingradius = tuple[float, None] #2
		self.scalefactor = tuple[float, None] #2
		self.sound = tuple[str, None] #2
		self.active = tuple[int, None] #2
		self.spritevolumeonly = 0 #2
		self.dmrgbtrack = tuple[str, None] #2
		self.sphere = "" #2
		self.sphereradius = 0.0 #2
		self.useboundingbox = 0 #2
		self.userdata = "" #2

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "CURRENTACTION?", 1)
		self.currentaction = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "LOCATION?", 6)
		self.location = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None), (float(records[4]) if records[4] != "NULL" else None), (float(records[5]) if records[5] != "NULL" else None), (float(records[6]) if records[6] != "NULL" else None)
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SCALEFACTOR?", 1)
		self.scalefactor = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SOUND?", 1)
		self.sound = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "ACTIVE?", 1)
		self.active = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SPRITEVOLUMEONLY", 1)
		self.spritevolumeonly = int(records[1])
		records = property(r, "DMRGBTRACK?", 1)
		self.dmrgbtrack = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SPHERE", 1)
		self.sphere = str(records[1])
		records = property(r, "SPHERERADIUS", 1)
		self.sphereradius = float(records[1])
		records = property(r, "USEBOUNDINGBOX", 1)
		self.useboundingbox = int(records[1])
		records = property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tCURRENTACTION? \"{self.currentaction}\"\n")
		w.write(f"\tLOCATION? \"{self.location}\"\n")
		w.write(f"\tBOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"\tSCALEFACTOR? \"{self.scalefactor}\"\n")
		w.write(f"\tSOUND? \"{self.sound}\"\n")
		w.write(f"\tACTIVE? \"{self.active}\"\n")
		w.write(f"\tSPRITEVOLUMEONLY \"{self.spritevolumeonly}\"\n")
		w.write(f"\tDMRGBTRACK? \"{self.dmrgbtrack}\"\n")
		w.write(f"\tSPHERE \"{self.sphere}\"\n")
		w.write(f"\tSPHERERADIUS \"{self.sphereradius}\"\n")
		w.write(f"\tUSEBOUNDINGBOX \"{self.useboundingbox}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		return ""

