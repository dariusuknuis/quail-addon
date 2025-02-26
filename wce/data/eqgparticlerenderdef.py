# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class eqgparticlerenderdef:
	@staticmethod
	def definition():
		return "EQGPARTICLERENDERDEF"

	tag:str
	version:int

	class render:
		render:int

		id2:int

		particlepoint:str

		unknowna1:int

		unknowna2:int

		unknowna3:int

		unknowna4:int

		unknowna5:int

		duration:int

		unknownb:int

		unknownffffffff:int

		unknownc:int

	renders:list[render]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "VERSION", 1)
		self.version = int(records[1])
		records = parse.property(r, "NUMRENDERS", 1)
		numrenders = int(records[1])

		self.renders = []
		for i in range(numrenders):
			renderi = self.render()
			records = parse.property(r, "RENDER", 1)
			renderi.render = int(records[1])
			records = parse.property(r, "ID2", 1)
			renderi.id2 = int(records[1])
			records = parse.property(r, "PARTICLEPOINT", 1)
			renderi.particlepoint = str(records[1])
			records = parse.property(r, "UNKNOWNA1", 1)
			renderi.unknowna1 = int(records[1])
			records = parse.property(r, "UNKNOWNA2", 1)
			renderi.unknowna2 = int(records[1])
			records = parse.property(r, "UNKNOWNA3", 1)
			renderi.unknowna3 = int(records[1])
			records = parse.property(r, "UNKNOWNA4", 1)
			renderi.unknowna4 = int(records[1])
			records = parse.property(r, "UNKNOWNA5", 1)
			renderi.unknowna5 = int(records[1])
			records = parse.property(r, "DURATION", 1)
			renderi.duration = int(records[1])
			records = parse.property(r, "UNKNOWNB", 1)
			renderi.unknownb = int(records[1])
			records = parse.property(r, "UNKNOWNFFFFFFFF", 1)
			renderi.unknownffffffff = int(records[1])
			records = parse.property(r, "UNKNOWNC", 1)
			renderi.unknownc = int(records[1])
			self.renders.append(renderi)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tVERSION \"{self.version}\"\n")
		w.write(f"\tNUMRENDERS \"{len(self.renders)}\"\n")
		for renderi in self.renders:
			w.write(f"\t\tRENDER \"{renderi.render}\"\n")
			w.write(f"\t\tID2 \"{renderi.id2}\"\n")
			w.write(f"\t\tPARTICLEPOINT \"{renderi.particlepoint}\"\n")
			w.write(f"\t\tUNKNOWNA1 \"{renderi.unknowna1}\"\n")
			w.write(f"\t\tUNKNOWNA2 \"{renderi.unknowna2}\"\n")
			w.write(f"\t\tUNKNOWNA3 \"{renderi.unknowna3}\"\n")
			w.write(f"\t\tUNKNOWNA4 \"{renderi.unknowna4}\"\n")
			w.write(f"\t\tUNKNOWNA5 \"{renderi.unknowna5}\"\n")
			w.write(f"\t\tDURATION \"{renderi.duration}\"\n")
			w.write(f"\t\tUNKNOWNB \"{renderi.unknownb}\"\n")
			w.write(f"\t\tUNKNOWNFFFFFFFF \"{renderi.unknownffffffff}\"\n")
			w.write(f"\t\tUNKNOWNC \"{renderi.unknownc}\"\n")

