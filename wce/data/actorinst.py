# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class actorinst:
	@staticmethod
	def definition():
		return "ACTORINST"

	tag:str
	definition:str # Reference to the actor's sprite tag
	currentaction:tuple[str, None] # The current action of the actor
	location:tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[int, None], tuple[int, None], tuple[int, None]] # The location of the actor
	boundingradius:tuple[float, None] # Radius around the actor instance for bounds
	scalefactor:tuple[float, None] # Scale factor of the actor instance
	sound:tuple[str, None] # Has a sound tag attached?
	active:tuple[int, None] # Is actor instance active?
	spritevolumeonly:tuple[int, None] # Uses sprite volume?
	dmrgbtrack:tuple[str, None] # References an RGB Track?
	sphere:str # Reference to sphere tag
	sphereradius:float # Radius of sphere
	useboundingbox:int # Use a bounding box
	userdata:int # Unknown property 2

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "DEFINITION", 1)
		self.definition = str(records[1])
		records = parse.property(r, "CURRENTACTION?", 1)
		self.currentaction = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "LOCATION?", 6)
		self.location = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None), (int(records[4]) if records[4] != "NULL" else None), (int(records[5]) if records[5] != "NULL" else None), (int(records[6]) if records[6] != "NULL" else None)
		records = parse.property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SCALEFACTOR?", 1)
		self.scalefactor = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SOUND?", 1)
		self.sound = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "ACTIVE?", 1)
		self.active = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SPRITEVOLUMEONLY?", 1)
		self.spritevolumeonly = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "DMRGBTRACK?", 1)
		self.dmrgbtrack = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SPHERE", 1)
		self.sphere = str(records[1])
		records = parse.property(r, "SPHERERADIUS", 1)
		self.sphereradius = float(records[1])
		records = parse.property(r, "USEBOUNDINGBOX", 1)
		self.useboundingbox = int(records[1])
		records = parse.property(r, "USERDATA", 1)
		self.userdata = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"DEFINITION \"{self.definition}\"\n")
		w.write(f"CURRENTACTION? \"{self.currentaction}\"\n")
		w.write(f"LOCATION? \"{self.location}\"\n")
		w.write(f"BOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"SCALEFACTOR? \"{self.scalefactor}\"\n")
		w.write(f"SOUND? \"{self.sound}\"\n")
		w.write(f"ACTIVE? \"{self.active}\"\n")
		w.write(f"SPRITEVOLUMEONLY? \"{self.spritevolumeonly}\"\n")
		w.write(f"DMRGBTRACK? \"{self.dmrgbtrack}\"\n")
		w.write(f"SPHERE \"{self.sphere}\"\n")
		w.write(f"SPHERERADIUS \"{self.sphereradius}\"\n")
		w.write(f"USEBOUNDINGBOX \"{self.useboundingbox}\"\n")
		w.write(f"USERDATA \"{self.userdata}\"\n")

