# Generated from quail, DO NOT EDIT
import io
from .parse import property

class lightdefinition:
	@staticmethod
	def definition():
		return "LIGHTDEFINITION"

	tag:str
	currentframe:int | None
	sleep:int | None
	haveskipframes:int
	skipframes:int

	def __init__(self):
		self.tag = ""
		self.currentframe = None #2
		self.sleep = None #2
		self.haveskipframes = 0 #2
		self.skipframes = 0 #2
		self.frames = []
		self.colors = []

	class lightlevels:
		lightlevels:float

		def __init__(self):
			self.lightlevels = 0.0 #3

	class color:
		color:tuple[float, float, float]

		def __init__(self):
			self.color = (0.0, 0.0, 0.0) #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "CURRENTFRAME?", 1)
		self.currentframe = int(records[1]) if records[1] != "NULL" else None
		records = property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.frames = []
		for i in range(numframes):
			lightlevelsi = type(self).lightlevels()
			records = property(r, "LIGHTLEVELS", 1)
			lightlevelsi.lightlevels = float(records[1])
			self.frames.append(lightlevelsi)
		records = property(r, "SLEEP?", 1)
		self.sleep = int(records[1]) if records[1] != "NULL" else None
		records = property(r, "HAVESKIPFRAMES", 1)
		self.haveskipframes = int(records[1])
		records = property(r, "SKIPFRAMES", 1)
		self.skipframes = int(records[1])
		records = property(r, "NUMCOLORS", 1)
		numcolors = int(records[1])

		self.colors = []
		for i in range(numcolors):
			colori = type(self).color()
			records = property(r, "COLOR", 3)
			colori.color = (float(records[1]), float(records[2]), float(records[3]))
			self.colors.append(colori)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tCURRENTFRAME? {('NULL' if self.currentframe is None else self.currentframe)}\n")
		w.write(f"\tNUMFRAMES {len(self.frames)}\n")
		for lightlevelsi in self.frames:
			w.write(f"\t\tLIGHTLEVELS {format(lightlevelsi.lightlevels, '.8e')}\n")
		w.write(f"\tSLEEP? {('NULL' if self.sleep is None else self.sleep)}\n")
		w.write(f"\tHAVESKIPFRAMES {self.haveskipframes}\n")
		w.write(f"\tSKIPFRAMES {self.skipframes}\n")
		w.write(f"\tNUMCOLORS {len(self.colors)}\n")
		for colori in self.colors:
			w.write(f"\t\tCOLOR {format(colori.color[0], '.8e')} {format(colori.color[1], '.8e')} {format(colori.color[2], '.8e')}\n")
		return ""

