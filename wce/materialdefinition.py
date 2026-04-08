# Generated from quail, DO NOT EDIT
import io
from .parse import property

class materialdefinition:
	@staticmethod
	def definition():
		return "MATERIALDEFINITION"

	tag:str
	variation:int
	rendermethod:str
	rgbpen:tuple[int, int, int, int]
	brightness:float
	scaledambient:float
	uvshiftperms:tuple[tuple[float, None], tuple[float, None]]
	twosided:int

	def __init__(self):
		self.tag = ""
		self.variation = 0 #2
		self.rendermethod = "" #2
		self.rgbpen = tuple[int, int, int, int] #2
		self.brightness = 0.0 #2
		self.scaledambient = 0.0 #2
		self.uvshiftperms = tuple[tuple[float, None], tuple[float, None]] #2
		self.twosided = 0 #2
		self.simplespriteinst = self.simplespriteinst()

	class simplespriteinst:
		simplespritetag:str
		simplespritehaveskipframes:int
		simplespriteskipframes:int

		def __init__(self):
			self.simplespritetag = "" #3
			self.simplespritehaveskipframes = 0 #3
			self.simplespriteskipframes = 0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

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
		self.simplespriteinst.simplespritetag = str(records[1])
		records = property(r, "SIMPLESPRITEHAVESKIPFRAMES", 1)
		self.simplespriteinst.simplespritehaveskipframes = int(records[1])
		records = property(r, "SIMPLESPRITESKIPFRAMES", 1)
		self.simplespriteinst.simplespriteskipframes = int(records[1])
		records = property(r, "UVSHIFTPERMS?", 2)
		self.uvshiftperms = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None)
		records = property(r, "TWOSIDED", 1)
		self.twosided = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVARIATION \"{self.variation}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tRGBPEN \"{self.rgbpen}\"\n")
		w.write(f"\tBRIGHTNESS \"{self.brightness}\"\n")
		w.write(f"\tSCALEDAMBIENT \"{self.scaledambient}\"\n")
		w.write(f"\tSIMPLESPRITEINST\n")
		w.write(f"\t\tSIMPLESPRITETAG \"{self.simplespriteinst.simplespritetag}\"\n")
		w.write(f"\t\tSIMPLESPRITEHAVESKIPFRAMES \"{self.simplespriteinst.simplespritehaveskipframes}\"\n")
		w.write(f"\t\tSIMPLESPRITESKIPFRAMES \"{self.simplespriteinst.simplespriteskipframes}\"\n")
		w.write(f"\tUVSHIFTPERMS? \"{self.uvshiftperms}\"\n")
		w.write(f"\tTWOSIDED \"{self.twosided}\"\n")
		return ""

