# Generated from quail, DO NOT EDIT
import io
from .parse import property

class trackdefinition:
	@staticmethod
	def definition():
		return "TRACKDEFINITION"

	tag:str
	tagindex:int

	def __init__(self):
		self.tag = ""
		self.tagindex = 0 #2
		self.frames = []
		self.legacyframes = []

	class frame:
		frame:tuple[int, int, int, int, int, int, int, int]

		def __init__(self):
			self.frame = tuple[int, int, int, int, int, int, int, int] #3

	class legacyframe:
		legacyframe:tuple[int, int, int, int, float, float, float, float]

		def __init__(self):
			self.legacyframe = tuple[int, int, int, int, float, float, float, float] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.frames = []
		for i in range(numframes):
			framei = type(self).frame()
			records = property(r, "FRAME", 8)
			framei.frame = int(records[1]), int(records[2]), int(records[3]), int(records[4]), int(records[5]), int(records[6]), int(records[7]), int(records[8])
			self.frames.append(framei)
		records = property(r, "NUMLEGACYFRAMES", 1)
		numlegacyframes = int(records[1])

		self.legacyframes = []
		for i in range(numlegacyframes):
			legacyframei = type(self).legacyframe()
			records = property(r, "LEGACYFRAME", 8)
			legacyframei.legacyframe = int(records[1]), int(records[2]), int(records[3]), int(records[4]), float(records[5]), float(records[6]), float(records[7]), float(records[8])
			self.legacyframes.append(legacyframei)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tNUMFRAMES \"{len(self.frames)}\"\n")
		for framei in self.frames:
			w.write(f"\t\tFRAME \"{framei.frame}\"\n")
		w.write(f"\tNUMLEGACYFRAMES \"{len(self.legacyframes)}\"\n")
		for legacyframei in self.legacyframes:
			w.write(f"\t\tLEGACYFRAME \"{legacyframei.legacyframe}\"\n")
		return ""

