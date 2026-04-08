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
	currentaction:tuple[str, None]
	location:tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[int, None], tuple[int, None], tuple[int, None]]
	activegeometry:tuple[str, None]
	spritevolumeonly:int
	userdata:str

	def __init__(self):
		self.tag = ""
		self.callback = "" #2
		self.boundsref = 0 #2
		self.currentaction = tuple[str, None] #2
		self.location = tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[int, None], tuple[int, None], tuple[int, None]] #2
		self.activegeometry = tuple[str, None] #2
		self.spritevolumeonly = 0 #2
		self.userdata = "" #2
		self.actions = []

	class action:
		unk1:int

		def __init__(self):
			self.unk1 = 0 #3
			self.levelsofdetails = []

		class levelofdetail:
			sprite:str
			mindistance:float

			def __init__(self):
				self.sprite = "" #4
				self.mindistance = 0.0 #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "CALLBACK", 1)
		self.callback = str(records[1])
		records = property(r, "BOUNDSREF", 1)
		self.boundsref = int(records[1])
		records = property(r, "CURRENTACTION?", 1)
		self.currentaction = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "LOCATION?", 6)
		self.location = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None), (int(records[4]) if records[4] != "NULL" else None), (int(records[5]) if records[5] != "NULL" else None), (int(records[6]) if records[6] != "NULL" else None)
		records = property(r, "ACTIVEGEOMETRY?", 1)
		self.activegeometry = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "NUMACTIONS", 1)
		numactions = int(records[1])

		self.actions = []
		for i in range(numactions):
			actioni = type(self).action()
			property(r, "ACTION", 0)

			records = property(r, "UNK1", 1)
			actioni.unk1 = int(records[1])
			records = property(r, "NUMLEVELSOFDETAILS", 1)
			numlevelsofdetails = int(records[1])

			actioni.levelsofdetails = []
			for j in range(numlevelsofdetails):
				levelofdetailj = type(actioni).levelofdetail()
				property(r, "LEVELOFDETAIL", 0)

				records = property(r, "SPRITE", 1)
				levelofdetailj.sprite = str(records[1])
				records = property(r, "MINDISTANCE", 1)
				levelofdetailj.mindistance = float(records[1])
				actioni.levelsofdetails.append(levelofdetailj)
			self.actions.append(actioni)
		records = property(r, "SPRITEVOLUMEONLY", 1)
		self.spritevolumeonly = int(records[1])
		records = property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tCALLBACK \"{self.callback}\"\n")
		w.write(f"\tBOUNDSREF \"{self.boundsref}\"\n")
		w.write(f"\tCURRENTACTION? \"{self.currentaction}\"\n")
		w.write(f"\tLOCATION? \"{self.location}\"\n")
		w.write(f"\tACTIVEGEOMETRY? \"{self.activegeometry}\"\n")
		w.write(f"\tNUMACTIONS \"{len(self.actions)}\"\n")
		for actioni in self.actions:
			w.write(f"\t\tACTION\n")
			w.write(f"\t\tUNK1 \"{actioni.unk1}\"\n")
			w.write(f"\t\tNUMLEVELSOFDETAILS \"{len(actioni.levelsofdetails)}\"\n")
			for levelofdetailj in actioni.levelsofdetails:
				w.write(f"\t\t\tLEVELOFDETAIL\n")
				w.write(f"\t\t\tSPRITE \"{levelofdetailj.sprite}\"\n")
				w.write(f"\t\t\tMINDISTANCE \"{levelofdetailj.mindistance}\"\n")
		w.write(f"\tSPRITEVOLUMEONLY \"{self.spritevolumeonly}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		return ""

