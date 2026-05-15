# Generated from quail, DO NOT EDIT
import io
from .parse import property

class dmtrackdef2:
	@staticmethod
	def definition():
		return "DMTRACKDEF2"

	tag:str
	sleep:int
	param2:int
	fpscale:int
	size6:int

	def __init__(self):
		self.tag = ""
		self.sleep = 0 #2
		self.param2 = 0 #2
		self.fpscale = 0 #2
		self.size6 = 0 #2
		self.frames = []

	class numvertices:

		def __init__(self):
			self.vertices = []

		class xyz:
			xyz:tuple[float, float, float]

			def __init__(self):
				self.xyz = (0.0, 0.0, 0.0) #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "SLEEP", 1)
		self.sleep = int(records[1])
		records = property(r, "PARAM2", 1)
		self.param2 = int(records[1])
		records = property(r, "FPSCALE", 1)
		self.fpscale = int(records[1])
		records = property(r, "SIZE6", 1)
		self.size6 = int(records[1])
		records = property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.frames = []
		for i in range(numframes):
			numverticesi = type(self).numvertices()
			records = property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			numverticesi.vertices = []
			for j in range(numvertices):
				xyzj = type(numverticesi).xyz()
				records = property(r, "XYZ", 3)
				xyzj.xyz = (float(records[1]), float(records[2]), float(records[3]))
				numverticesi.vertices.append(xyzj)
			self.frames.append(numverticesi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSLEEP {self.sleep}\n")
		w.write(f"\tPARAM2 {self.param2}\n")
		w.write(f"\tFPSCALE {self.fpscale}\n")
		w.write(f"\tSIZE6 {self.size6}\n")
		w.write(f"\tNUMFRAMES {len(self.frames)}\n")
		for numverticesi in self.frames:
			w.write(f"\t\tNUMVERTICES {len(numverticesi.vertices)}\n")
			for xyzj in numverticesi.vertices:
				w.write(f"\t\t\tXYZ {format(xyzj.xyz[0], '.8e')} {format(xyzj.xyz[1], '.8e')} {format(xyzj.xyz[2], '.8e')}\n")
		return ""

