# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class dmtrackdef2:
	@staticmethod
	def definition():
		return "DMTRACKDEF2"

	tag:str
	sleep:int
	param2:int
	fpscale:int
	size6:int

	class numvertices:

		class xyz:
			xyz:tuple[float, float, float]

		xyzs:list[xyz]

	numverticess:list[numvertices]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "SLEEP", 1)
		self.sleep = int(records[1])
		records = parse.property(r, "PARAM2", 1)
		self.param2 = int(records[1])
		records = parse.property(r, "FPSCALE", 1)
		self.fpscale = int(records[1])
		records = parse.property(r, "SIZE6", 1)
		self.size6 = int(records[1])
		records = parse.property(r, "NUMFRAMES", 1)
		numframes = int(records[1])

		self.numverticess = []
		for i in range(numframes):
			numverticesi = self.numvertices()
			records = parse.property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			numverticesi.xyzs = []
			for j in range(numvertices):
				xyzj = self.numvertices.xyz()
				records = parse.property(r, "XYZ", 3)
				xyzj.xyz = float(records[1]), float(records[2]), float(records[3])
				numverticesi.xyzs.append(xyzj)
			self.numverticess.append(numverticesi)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSLEEP \"{self.sleep}\"\n")
		w.write(f"\tPARAM2 \"{self.param2}\"\n")
		w.write(f"\tFPSCALE \"{self.fpscale}\"\n")
		w.write(f"\tSIZE6 \"{self.size6}\"\n")
		w.write(f"\tNUMFRAMES \"{len(self.numverticess)}\"\n")
		for numverticesi in self.numverticess:
			w.write(f"\t\tNUMVERTICES \"{len(numverticesi.xyzs)}\"\n")
			for xyzj in numverticesi.xyzs:
				w.write(f"\t\t\tXYZ \"{xyzj.xyz}\"\n")

