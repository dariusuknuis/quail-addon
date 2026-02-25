# Generated from quail, DO NOT EDIT
import io
from .parse import property

class simplespritedef:
	@staticmethod
	def definition():
		return "SIMPLESPRITEDEF"

	tag:str
	tagindex:int
	variation:int
	skipframes:int
	sleep:tuple[int, None]
	currentframe:tuple[int, None]

	def __init__(self):
		self.tag = ""
		self.tagindex = 0 #2
		self.variation = 0 #2
		self.skipframes = 0 #2
		self.sleep = tuple[int, None] #2
		self.currentframe = tuple[int, None] #2
		self.frames = []

	class frame:
		frame:str

		def __init__(self):
			self.frame = "" #3
			self.files = []

		class file:
			file:str

			def __init__(self):
				self.file = "" #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = property(r, "VARIATION", 1)
		self.variation = int(records[1])
		records = property(r, "SKIPFRAMES", 1)
		self.skipframes = int(records[1])
		records = property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "CURRENTFRAME?", 1)
		self.currentframe = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.frames = []
		for i in range(numframes):
			framei = type(self).frame()
			records = property(r, "FRAME", 1)
			framei.frame = str(records[1])
			records = property(r, "NUMFILES", 1)
			numfiles = int(records[1])

			framei.files = []
			for j in range(numfiles):
				filej = type(framei).file()
				records = property(r, "FILE", 1)
				filej.file = str(records[1])
				framei.files.append(filej)
			self.frames.append(framei)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tTAGINDEX \"{self.tagindex}\"\n")
		w.write(f"\tVARIATION \"{self.variation}\"\n")
		w.write(f"\tSKIPFRAMES \"{self.skipframes}\"\n")
		w.write(f"\tSLEEP? \"{self.sleep}\"\n")
		w.write(f"\tCURRENTFRAME? \"{self.currentframe}\"\n")
		w.write(f"\tNUMFRAMES \"{len(self.frames)}\"\n")
		for framei in self.frames:
			w.write(f"\t\tFRAME \"{framei.frame}\"\n")
			w.write(f"\t\tNUMFILES \"{len(framei.files)}\"\n")
			for filej in framei.files:
				w.write(f"\t\t\tFILE \"{filej.file}\"\n")
		return ""

