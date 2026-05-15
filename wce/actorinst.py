# Generated from quail, DO NOT EDIT
import io
from .parse import property

class actorinst:
	@staticmethod
	def definition():
		return "ACTORINST"

	tag:str
	sprite:str
	currentaction:str | None
	location:tuple[float, float, float, float, float, float] | None
	boundingradius:float | None
	scalefactor:float | None
	sound:str | None
	active:int | None
	spritevolumeonly:int
	dmrgbtrack:str | None
	sphere:str
	sphereradius:float
	useboundingbox:int
	userdata:str

	def __init__(self):
		self.tag = ""
		self.sprite = "" #2
		self.currentaction = None #2
		self.location = None #2
		self.boundingradius = None #2
		self.scalefactor = None #2
		self.sound = None #2
		self.active = None #2
		self.spritevolumeonly = 0 #2
		self.dmrgbtrack = None #2
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
		self.currentaction = str(records[1]) if records[1] != "NULL" else None
		records = property(r, "LOCATION?", 6)
		self.location = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]), float(records[4]), float(records[5]), float(records[6]))
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = float(records[1]) if records[1] != "NULL" else None
		records = property(r, "SCALEFACTOR?", 1)
		self.scalefactor = float(records[1]) if records[1] != "NULL" else None
		records = property(r, "SOUND?", 1)
		self.sound = str(records[1]) if records[1] != "NULL" else None
		records = property(r, "ACTIVE?", 1)
		self.active = int(records[1]) if records[1] != "NULL" else None
		records = property(r, "SPRITEVOLUMEONLY", 1)
		self.spritevolumeonly = int(records[1])
		records = property(r, "DMRGBTRACK?", 1)
		self.dmrgbtrack = str(records[1]) if records[1] != "NULL" else None
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
		if self.currentaction is None: w.write("\tCURRENTACTION? NULL\n")
		else: w.write(f"\tCURRENTACTION? \"{self.currentaction}\"\n")
		w.write(f"\tLOCATION? {('NULL' if self.location is None else format(self.location[0], '.8e'))} {('NULL' if self.location is None else format(self.location[1], '.8e'))} {('NULL' if self.location is None else format(self.location[2], '.8e'))} {('NULL' if self.location is None else format(self.location[3], '.8e'))} {('NULL' if self.location is None else format(self.location[4], '.8e'))} {('NULL' if self.location is None else format(self.location[5], '.8e'))}\n")
		w.write(f"\tBOUNDINGRADIUS? {('NULL' if self.boundingradius is None else format(self.boundingradius, '.8e'))}\n")
		w.write(f"\tSCALEFACTOR? {('NULL' if self.scalefactor is None else format(self.scalefactor, '.8e'))}\n")
		if self.sound is None: w.write("\tSOUND? NULL\n")
		else: w.write(f"\tSOUND? \"{self.sound}\"\n")
		w.write(f"\tACTIVE? {('NULL' if self.active is None else self.active)}\n")
		w.write(f"\tSPRITEVOLUMEONLY {self.spritevolumeonly}\n")
		if self.dmrgbtrack is None: w.write("\tDMRGBTRACK? NULL\n")
		else: w.write(f"\tDMRGBTRACK? \"{self.dmrgbtrack}\"\n")
		w.write(f"\tSPHERE \"{self.sphere}\"\n")
		w.write(f"\tSPHERERADIUS {format(self.sphereradius, '.8e')}\n")
		w.write(f"\tUSEBOUNDINGBOX {self.useboundingbox}\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		return ""

