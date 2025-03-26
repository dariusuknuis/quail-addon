# Generated from quail, DO NOT EDIT
import io
from .parse import property

class materialdefinition:
	@staticmethod
	def definition():
		return "MATERIALDEFINITION"

	tag:str
	tagindex:int # For tag variations, starts at 0, increases by 1
	variation:int # For variations
	rendermethod:str # Method for rendering
	rgbpen:tuple[int, int, int, int] # RGB Colorizing
	brightness:float # Color brightness
	scaledambient:float # Scaled ambient amount
	simplespritetag:str # Simple sprite instance tag
	simplespritetagindex:int
	simplespritehexfiftyflag:int # Hex fifty flag
	pairs:list[str] # Pairs of flags?
	doublesided:int # Is material double sided?

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "VARIATION", 1)
		self.variation = int(records[1])
		records = property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		records = property(r, "RGBPEN", 4)
		self.rgbpen = int(records[1]), int(records[2]), int(records[3]), int(records[4])
		records = property(r, "BRIGHTNESS", 1)
		self.brightness = float(records[1])
		records = property(r, "SCALEDAMBIENT", 1)
		self.scaledambient = float(records[1])
		property(r, "SIMPLESPRITEINST", 0)

		records = property(r, "SIMPLESPRITETAG", 1)
		self.simplespritetag = str(records[1])
		records = property(r, "SIMPLESPRITETAGINDEX", 1)
		self.simplespritetagindex = int(records[1])
		records = property(r, "SIMPLESPRITEHEXFIFTYFLAG", 1)
		self.simplespritehexfiftyflag = int(records[1])
		records = property(r, "PAIRS?", -1)
		self.pairs = records[1:]

		records = property(r, "DOUBLESIDED", 1)
		self.doublesided = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tVARIATION \"{self.variation}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tRGBPEN \"{self.rgbpen}\"\n")
		w.write(f"\tBRIGHTNESS \"{self.brightness}\"\n")
		w.write(f"\tSCALEDAMBIENT \"{self.scaledambient}\"\n")
		w.write(f"\tSIMPLESPRITEINST\n")
		w.write(f"\tSIMPLESPRITETAG \"{self.simplespritetag}\"\n")
		w.write(f"\tSIMPLESPRITETAGINDEX \"{self.simplespritetagindex}\"\n")
		w.write(f"\tSIMPLESPRITEHEXFIFTYFLAG \"{self.simplespritehexfiftyflag}\"\n")
		w.write(f"PAIRS? \"{self.pairs}\"\n")
		w.write(f"\tDOUBLESIDED \"{self.doublesided}\"\n")

