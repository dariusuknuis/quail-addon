# Generated from quail, DO NOT EDIT
import io
from .parse import property

class actordef:
	@staticmethod
	def definition():
		return "ACTORDEF"

	tag:str
	callback:str
	boundsref:int
	currentaction:int | None
	location:tuple[float, float, float, int, int, int] | None
	activegeometry:str | None
	spritevolumeonly:int
	userdata:str

	def __init__(self):
		self.tag = ""
		self.callback = "" #2
		self.boundsref = 0 #2
		self.currentaction = None #2
		self.location = None #2
		self.activegeometry = None #2
		self.spritevolumeonly = 0 #2
		self.userdata = "" #2
		self.actions = []

	class action:

		def __init__(self):
			self.action = self.action()

		class action:
			unk1:int

			def __init__(self):
				self.unk1 = 0 #4
				self.levelsofdetails = []

			class levelofdetail:

				def __init__(self):
					self.levelofdetail = self.levelofdetail()

				class levelofdetail:
					sprite:str
					mindistance:float

					def __init__(self):
						self.sprite = "" #6
						self.mindistance = 0.0 #6

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "CALLBACK", 1)
		self.callback = str(records[1])
		records = property(r, "BOUNDSREF", 1)
		self.boundsref = int(records[1])
		records = property(r, "CURRENTACTION?", 1)
		self.currentaction = int(records[1]) if records[1] != "NULL" else None
		records = property(r, "LOCATION?", 6)
		self.location = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]), int(records[4]), int(records[5]), int(records[6]))
		records = property(r, "ACTIVEGEOMETRY?", 1)
		self.activegeometry = str(records[1]) if records[1] != "NULL" else None
		records = property(r, "NUMACTIONS", 1)
		numactions = int(records[1])

		self.actions = []
		for i in range(numactions):
			actioni = type(self).action()
			property(r, "ACTION", 0)

			records = property(r, "UNK1", 1)
			actioni.action.unk1 = int(records[1])
			records = property(r, "NUMLEVELSOFDETAILS", 1)
			numlevelsofdetails = int(records[1])

			actioni.action.levelsofdetails = []
			for j in range(numlevelsofdetails):
				levelofdetailj = type(actioni.action).levelofdetail()
				property(r, "LEVELOFDETAIL", 0)

				records = property(r, "SPRITE", 1)
				levelofdetailj.levelofdetail.sprite = str(records[1])
				records = property(r, "MINDISTANCE", 1)
				levelofdetailj.levelofdetail.mindistance = float(records[1])
				actioni.action.levelsofdetails.append(levelofdetailj)
			self.actions.append(actioni)
		records = property(r, "SPRITEVOLUMEONLY", 1)
		self.spritevolumeonly = int(records[1])
		records = property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tCALLBACK \"{self.callback}\"\n")
		w.write(f"\tBOUNDSREF {self.boundsref}\n")
		w.write(f"\tCURRENTACTION? {('NULL' if self.currentaction is None else self.currentaction)}\n")
		w.write(f"\tLOCATION? {('NULL' if self.location is None else self.location[0])} {('NULL' if self.location is None else self.location[1])} {('NULL' if self.location is None else self.location[2])} {('NULL' if self.location is None else self.location[3])} {('NULL' if self.location is None else self.location[4])} {('NULL' if self.location is None else self.location[5])}\n")
		if self.activegeometry is None: w.write("\tACTIVEGEOMETRY? NULL\n")
		else: w.write(f"\tACTIVEGEOMETRY? \"{self.activegeometry}\"\n")
		w.write(f"\tNUMACTIONS {len(self.actions)}\n")
		for actioni in self.actions:
			w.write(f"\t\tACTION\n")
			w.write(f"\t\t\tUNK1 {actioni.action.unk1}\n")
			w.write(f"\t\t\tNUMLEVELSOFDETAILS {len(actioni.action.levelsofdetails)}\n")
			for levelofdetailj in actioni.action.levelsofdetails:
				w.write(f"\t\t\t\tLEVELOFDETAIL\n")
				w.write(f"\t\t\t\t\tSPRITE \"{levelofdetailj.levelofdetail.sprite}\"\n")
				w.write(f"\t\t\t\t\tMINDISTANCE {format(levelofdetailj.levelofdetail.mindistance, '.8e')}\n")
		w.write(f"\tSPRITEVOLUMEONLY {self.spritevolumeonly}\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		return ""

