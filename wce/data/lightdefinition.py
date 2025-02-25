# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class lightdefinition:
	@staticmethod
	def definition():
		return "LIGHTDEFINITION"

	tag:str
	currentframe:tuple[int, None] # Is there a current frame, and what's value

	class lightlevels:
		lightlevels:float # value of light level frame

	lightlevelss:list[lightlevels]
	sleep:tuple[int, None] # Is a sleep value set?
	skipframes:int # Are frames skipped

	class color:
		color:tuple[float, float, float] # Color value

	colors:list[color]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "CURRENTFRAME?", 1)
		self.currentframe = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.lightlevelss = []
		for i in range(numframes):
			lightlevelsi = self.lightlevels()
			records = parse.property(r, "LIGHTLEVELS", 1)
			lightlevelsi.lightlevels = float(records[1])
			self.lightlevelss.append(lightlevelsi)
		records = parse.property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SKIPFRAMES", 1)
		self.skipframes = int(records[1])
		records = parse.property(r, "NUMCOLORS", 1)
		numcolors = int(records[1])

		self.colors = []
		for i in range(numcolors):
			colori = self.color()
			records = parse.property(r, "COLOR", 3)
			colori.color = float(records[1]), float(records[2]), float(records[3])
			self.colors.append(colori)

	def write(self, w:io.TextIOWrapper):
		w.write(f"CURRENTFRAME? \"{self.currentframe}\"\n")
		w.write(f"NUMFRAMES \"{len(self.lightlevelss)}\"\n")
		for lightlevelsi in self.lightlevelss:
			w.write(f"LIGHTLEVELS \"{lightlevelsi.lightlevels}\"\n")
		w.write(f"SLEEP? \"{self.sleep}\"\n")
		w.write(f"SKIPFRAMES \"{self.skipframes}\"\n")
		w.write(f"NUMCOLORS \"{len(self.colors)}\"\n")
		for colori in self.colors:
			w.write(f"COLOR \"{colori.color}\"\n")

