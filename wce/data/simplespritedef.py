# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class simplespritedef:
	@staticmethod
	def definition():
		return "SIMPLESPRITEDEF"

	tag:str
	tagindex:int # Index of tag
	variation:int # Variation of tag
	skipframes:tuple[int, None] # Should frames be skipped?
	animated:tuple[int, None] # Is animated?
	sleep:tuple[int, None] # Is there a sleep duration (in milliseconds)
	currentframe:tuple[int, None] # Current frame set?

	class frame:
		frame:str # Frame tag


		class file:
			file:str # Texture file name

		files:list[file]

	frames:list[frame]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "TAGINDEX", 1)
		self.tagindex = int(records[1])
		records = parse.property(r, "VARIATION", 1)
		self.variation = int(records[1])
		records = parse.property(r, "SKIPFRAMES?", 1)
		self.skipframes = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "ANIMATED?", 1)
		self.animated = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "CURRENTFRAME?", 1)
		self.currentframe = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.frames = []
		for i in range(numframes):
			framei = self.frame()
			records = parse.property(r, "FRAME", 1)
			framei.frame = str(records[1])
			records = parse.property(r, "NUMFILES", 1)
			numfiles = int(records[1])

			framei.files = []
			for j in range(numfiles):
				filej = self.frame.file()
				records = parse.property(r, "FILE", 1)
				filej.file = str(records[1])
				framei.files.append(filej)
			self.frames.append(framei)

	def write(self, w:io.TextIOWrapper):
		w.write(f"TAGINDEX \"{self.tagindex}\"\n")
		w.write(f"VARIATION \"{self.variation}\"\n")
		w.write(f"SKIPFRAMES? \"{self.skipframes}\"\n")
		w.write(f"ANIMATED? \"{self.animated}\"\n")
		w.write(f"SLEEP? \"{self.sleep}\"\n")
		w.write(f"CURRENTFRAME? \"{self.currentframe}\"\n")
		w.write(f"NUMFRAMES \"{len(self.frames)}\"\n")
		for framei in self.frames:
			w.write(f"FRAME \"{framei.frame}\"\n")
			w.write(f"NUMFILES \"{len(framei.files)}\"\n")
			for filej in framei.files:
				w.write(f"FILE \"{filej.file}\"\n")

