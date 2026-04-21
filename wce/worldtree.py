# Generated from quail, DO NOT EDIT
import io
from .parse import property

class worldtree:
	@staticmethod
	def definition():
		return "WORLDTREE"

	tag:str

	def __init__(self):
		self.tag = ""
		self.worldnodes = []

	class worldnode:
		normalabcd:tuple[float, float, float, float]
		worldregiontag:str
		fronttree:int
		backtree:int

		def __init__(self):
			self.normalabcd = (0.0, 0.0, 0.0, 0.0) #3
			self.worldregiontag = "" #3
			self.fronttree = 0 #3
			self.backtree = 0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NUMWORLDNODES", 1)
		numworldnodes = int(records[1])

		self.worldnodes = []
		for i in range(numworldnodes):
			worldnodei = type(self).worldnode()
			property(r, "WORLDNODE", 0)

			records = property(r, "NORMALABCD", 4)
			worldnodei.normalabcd = (float(records[1]), float(records[2]), float(records[3]), float(records[4]))
			records = property(r, "WORLDREGIONTAG", 1)
			worldnodei.worldregiontag = str(records[1])
			records = property(r, "FRONTTREE", 1)
			worldnodei.fronttree = int(records[1])
			records = property(r, "BACKTREE", 1)
			worldnodei.backtree = int(records[1])
			self.worldnodes.append(worldnodei)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMWORLDNODES \"{len(self.worldnodes)}\"\n")
		for worldnodei in self.worldnodes:
			w.write(f"\t\tWORLDNODE\n")
			w.write(f"\t\tNORMALABCD {worldnodei.normalabcd[0]} {worldnodei.normalabcd[1]} {worldnodei.normalabcd[2]} {worldnodei.normalabcd[3]}\n")
			w.write(f"\t\tWORLDREGIONTAG \"{worldnodei.worldregiontag}\"\n")
			w.write(f"\t\tFRONTTREE {worldnodei.fronttree}\n")
			w.write(f"\t\tBACKTREE {worldnodei.backtree}\n")
		return ""

