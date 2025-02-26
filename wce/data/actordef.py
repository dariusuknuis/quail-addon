# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class actordef:
	@staticmethod
	def definition():
		return "ACTORDEF"

	tag:str
	callback:str # The callback function for the actor
	boundsref:int # The bounds reference for the actor
	currentaction:tuple[str, None] # The current action of the actor
	location:tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[int, None], tuple[int, None], tuple[int, None]] # The location of the actor
	activegeometry:tuple[str, None] # The active geometry of the actor

	class action:

		unk1:int # Unknown entry 1


		class levelofdetail:

			sprite:str # Sprite entry tag

			spriteindex:int # Sprite index

			mindistance:float # Minimum distance to render LOD

		levelofdetails:list[levelofdetail]

	actions:list[action]
	usemodelcollider:int # Ignored in RoF2. 0x80 flag. This gets ignored if ActorInst doesn't have it. Likely need to use hierarchysprite flag for things like boats
	userdata:int # Unknown property 2

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "CALLBACK", 1)
		self.callback = str(records[1])
		records = parse.property(r, "BOUNDSREF", 1)
		self.boundsref = int(records[1])
		records = parse.property(r, "CURRENTACTION?", 1)
		self.currentaction = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "LOCATION?", 6)
		self.location = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None), (int(records[4]) if records[4] != "NULL" else None), (int(records[5]) if records[5] != "NULL" else None), (int(records[6]) if records[6] != "NULL" else None)
		records = parse.property(r, "ACTIVEGEOMETRY?", 1)
		self.activegeometry = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "NUMACTIONS", 1)
		numactions = int(records[1])

		self.actions = []
		for i in range(numactions):
			actioni = self.action()
			parse.property(r, "ACTION", 0)

			records = parse.property(r, "UNK1", 1)
			actioni.unk1 = int(records[1])
			records = parse.property(r, "NUMLEVELSOFDETAIL", 1)
			numlevelsofdetail = int(records[1])

			actioni.levelofdetails = []
			for j in range(numlevelsofdetail):
				levelofdetailj = self.action.levelofdetail()
				parse.property(r, "LEVELOFDETAIL", 0)

				records = parse.property(r, "SPRITE", 1)
				levelofdetailj.sprite = str(records[1])
				records = parse.property(r, "SPRITEINDEX", 1)
				levelofdetailj.spriteindex = int(records[1])
				records = parse.property(r, "MINDISTANCE", 1)
				levelofdetailj.mindistance = float(records[1])
				actioni.levelofdetails.append(levelofdetailj)
			self.actions.append(actioni)
		records = parse.property(r, "USEMODELCOLLIDER", 1)
		self.usemodelcollider = int(records[1])
		records = parse.property(r, "USERDATA", 1)
		self.userdata = int(records[1])

	def write(self, w:io.TextIOWrapper):
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
			w.write(f"\t\tNUMLEVELSOFDETAIL \"{len(actioni.levelofdetails)}\"\n")
			for levelofdetailj in actioni.levelofdetails:
				w.write(f"\t\t\tLEVELOFDETAIL\n")
				w.write(f"\t\t\tSPRITE \"{levelofdetailj.sprite}\"\n")
				w.write(f"\t\t\tSPRITEINDEX \"{levelofdetailj.spriteindex}\"\n")
				w.write(f"\t\t\tMINDISTANCE \"{levelofdetailj.mindistance}\"\n")
		w.write(f"\tUSEMODELCOLLIDER \"{self.usemodelcollider}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")

