# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class worldtree:
	@staticmethod
	def definition():
		return "WORLDTREE"

	tag:str

	class worldnode:

		normalabcd:tuple[float, float, float, float]

		worldregiontag:str

		fronttree:int

		backtree:int

	worldnodes:list[worldnode]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "NUMWORLDNODES", 1)
		numworldnodes = int(records[1])

		self.worldnodes = []
		for i in range(numworldnodes):
			worldnodei = self.worldnode()
			parse.property(r, "WORLDNODE", 0)

			records = parse.property(r, "NORMALABCD", 4)
			worldnodei.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = parse.property(r, "WORLDREGIONTAG", 1)
			worldnodei.worldregiontag = str(records[1])
			records = parse.property(r, "FRONTTREE", 1)
			worldnodei.fronttree = int(records[1])
			records = parse.property(r, "BACKTREE", 1)
			worldnodei.backtree = int(records[1])
			self.worldnodes.append(worldnodei)

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMWORLDNODES \"{len(self.worldnodes)}\"\n")
		for worldnodei in self.worldnodes:
			w.write(f"\t\tWORLDNODE\n")
			w.write(f"\t\tNORMALABCD \"{worldnodei.normalabcd}\"\n")
			w.write(f"\t\tWORLDREGIONTAG \"{worldnodei.worldregiontag}\"\n")
			w.write(f"\t\tFRONTTREE \"{worldnodei.fronttree}\"\n")
			w.write(f"\t\tBACKTREE \"{worldnodei.backtree}\"\n")

