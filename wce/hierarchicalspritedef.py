# Generated from quail, DO NOT EDIT
import io
from .parse import property

class hierarchicalspritedef:
	@staticmethod
	def definition():
		return "HIERARCHICALSPRITEDEF"

	tag:str
	sprite:str
	centeroffset:tuple[float, float, float] | None
	boundingradius:float | None
	haveattachedskins:int
	dagcollisions:int

	def __init__(self):
		self.tag = ""
		self.sprite = "" #2
		self.centeroffset = None #2
		self.boundingradius = None #2
		self.haveattachedskins = 0 #2
		self.dagcollisions = 0 #2
		self.dags = []
		self.attachedskins = []

	class dag:
		tag:str
		spritetag:str
		track:str
		subdaglist:list[str]

		def __init__(self):
			self.tag = "" #3
			self.spritetag = "" #3
			self.track = "" #3
			self.subdaglist = [] #3

	class attachedskin:
		dmsprite:str
		linkskinupdatestodagindex:int

		def __init__(self):
			self.dmsprite = "" #3
			self.linkskinupdatestodagindex = 0 #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "NUMDAGS", 1)
		numdags = int(records[1])

		self.dags = []
		for i in range(numdags):
			dagi = type(self).dag()
			property(r, "DAG", 0)

			records = property(r, "TAG", 1)
			dagi.tag = str(records[1])
			records = property(r, "SPRITETAG", 1)
			dagi.spritetag = str(records[1])
			records = property(r, "TRACK", 1)
			dagi.track = str(records[1])
			records = property(r, "SUBDAGLIST", -1)
			dagi.subdaglist = records[1:]

			self.dags.append(dagi)
		records = property(r, "NUMATTACHEDSKINS", 1)
		numattachedskins = int(records[1])

		self.attachedskins = []
		for i in range(numattachedskins):
			attachedskini = type(self).attachedskin()
			property(r, "ATTACHEDSKIN", 0)

			records = property(r, "DMSPRITE", 1)
			attachedskini.dmsprite = str(records[1])
			records = property(r, "LINKSKINUPDATESTODAGINDEX", 1)
			attachedskini.linkskinupdatestodagindex = int(records[1])
			self.attachedskins.append(attachedskini)
		property(r, "POLYHEDRON", 0)

		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		records = property(r, "CENTEROFFSET?", 3)
		self.centeroffset = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = float(records[1]) if records[1] != "NULL" else None
		records = property(r, "HAVEATTACHEDSKINS", 1)
		self.haveattachedskins = int(records[1])
		records = property(r, "DAGCOLLISIONS", 1)
		self.dagcollisions = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tNUMDAGS {len(self.dags)}\n")
		for dagi in self.dags:
			w.write(f"\t\tDAG\n")
			w.write(f"\t\tTAG \"{dagi.tag}\"\n")
			w.write(f"\t\tSPRITETAG \"{dagi.spritetag}\"\n")
			w.write(f"\t\tTRACK \"{dagi.track}\"\n")
			w.write(f"\t\tSUBDAGLIST {dagi.subdaglist}\n")
		w.write(f"\tNUMATTACHEDSKINS {len(self.attachedskins)}\n")
		for attachedskini in self.attachedskins:
			w.write(f"\t\tATTACHEDSKIN\n")
			w.write(f"\t\tDMSPRITE \"{attachedskini.dmsprite}\"\n")
			w.write(f"\t\tLINKSKINUPDATESTODAGINDEX {attachedskini.linkskinupdatestodagindex}\n")
		w.write(f"\tPOLYHEDRON\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		w.write(f"\tCENTEROFFSET? {('NULL' if self.centeroffset is None else self.centeroffset[0])} {('NULL' if self.centeroffset is None else self.centeroffset[1])} {('NULL' if self.centeroffset is None else self.centeroffset[2])}\n")
		w.write(f"\tBOUNDINGRADIUS? {('NULL' if self.boundingradius is None else format(self.boundingradius, '.8e'))}\n")
		w.write(f"\tHAVEATTACHEDSKINS {self.haveattachedskins}\n")
		w.write(f"\tDAGCOLLISIONS {self.dagcollisions}\n")
		return ""

