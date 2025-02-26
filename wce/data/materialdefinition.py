# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

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
	tag:str # Simple sprite instance tag
	hexfiftyflag:int # Hex fifty flag
	pairs:tuple[tuple[int, None], tuple[int, None]] # Pairs of flags?
	doublesided:int # Is material double sided?

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "VARIATION", 1)
		self.variation = int(records[1])
		records = parse.property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		records = parse.property(r, "RGBPEN", 4)
		self.rgbpen = int(records[1]), int(records[2]), int(records[3]), int(records[4])
		records = parse.property(r, "BRIGHTNESS", 1)
		self.brightness = float(records[1])
		records = parse.property(r, "SCALEDAMBIENT", 1)
		self.scaledambient = float(records[1])
		parse.property(r, "SIMPLESPRITEINST", 0)

		records = parse.property(r, "TAG", 1)
		self.tag = str(records[1])
		records = parse.property(r, "HEXFIFTYFLAG", 1)
		self.hexfiftyflag = int(records[1])
		records = parse.property(r, "PAIRS?", 2)
		self.pairs = (int(records[1]) if records[1] != "NULL" else None), (int(records[2]) if records[2] != "NULL" else None)
		records = parse.property(r, "DOUBLESIDED", 1)
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
		w.write(f"\tTAG \"{self.tag}\"\n")
		w.write(f"\tHEXFIFTYFLAG \"{self.hexfiftyflag}\"\n")
		w.write(f"\tPAIRS? \"{self.pairs}\"\n")
		w.write(f"\tDOUBLESIDED \"{self.doublesided}\"\n")

