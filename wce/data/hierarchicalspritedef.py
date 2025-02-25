# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class hierarchicalspritedef:
	@staticmethod
	def definition():
		return "HIERARCHICALSPRITEDEF"

	tag:str

	class dag:

		tag:str

		sprite:str

		spriteindex:int

		track:str

		trackindex:str

		subdaglist:list[str]

	dags:list[dag]

	class attachedskin:

		dmsprite:str

		dmspriteindex:int

		linkskinupdatestodagindex:int

	attachedskins:list[attachedskin]
	definition:str
	centeroffset:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boundingradius:tuple[float, None]
	hextwohundredflag:int # also known as HAVEATTACHEDSKINS
	hextwentythousandflag:int # also known as DAGCOLLISONS

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "NUMDAGS", 1)
		numdags = int(records[1])

		self.dags = []
		for i in range(numdags):
			dagi = self.dag()
			parse.property(r, "DAG", 0)

			records = parse.property(r, "TAG", 1)
			dagi.tag = str(records[1])
			records = parse.property(r, "SPRITE", 1)
			dagi.sprite = str(records[1])
			records = parse.property(r, "SPRITEINDEX", 1)
			dagi.spriteindex = int(records[1])
			records = parse.property(r, "TRACK", 1)
			dagi.track = str(records[1])
			records = parse.property(r, "TRACKINDEX", 1)
			dagi.trackindex = str(records[1])
			records = parse.property(r, "SUBDAGLIST", -1)
			dagi.subdaglist = records[1:]

			self.dags.append(dagi)
		records = parse.property(r, "NUMATTACHEDSKINS", 1)
		numattachedskins = int(records[1])

		self.attachedskins = []
		for i in range(numattachedskins):
			attachedskini = self.attachedskin()
			parse.property(r, "ATTACHEDSKIN", 0)

			records = parse.property(r, "DMSPRITE", 1)
			attachedskini.dmsprite = str(records[1])
			records = parse.property(r, "DMSPRITEINDEX", 1)
			attachedskini.dmspriteindex = int(records[1])
			records = parse.property(r, "LINKSKINUPDATESTODAGINDEX", 1)
			attachedskini.linkskinupdatestodagindex = int(records[1])
			self.attachedskins.append(attachedskini)
		parse.property(r, "POLYHEDRON", 0)

		records = parse.property(r, "DEFINITION", 1)
		self.definition = str(records[1])
		records = parse.property(r, "CENTEROFFSET?", 3)
		self.centeroffset = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "HEXTWOHUNDREDFLAG", 1)
		self.hextwohundredflag = int(records[1])
		records = parse.property(r, "HEXTWENTYTHOUSANDFLAG", 1)
		self.hextwentythousandflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"NUMDAGS \"{len(self.dags)}\"\n")
		for dagi in self.dags:
			w.write(f"DAG\n")
			w.write(f"TAG \"{dagi.tag}\"\n")
			w.write(f"SPRITE \"{dagi.sprite}\"\n")
			w.write(f"SPRITEINDEX \"{dagi.spriteindex}\"\n")
			w.write(f"TRACK \"{dagi.track}\"\n")
			w.write(f"TRACKINDEX \"{dagi.trackindex}\"\n")
			w.write(f"SUBDAGLIST \"{dagi.subdaglist}\"\n")
		w.write(f"NUMATTACHEDSKINS \"{len(self.attachedskins)}\"\n")
		for attachedskini in self.attachedskins:
			w.write(f"ATTACHEDSKIN\n")
			w.write(f"DMSPRITE \"{attachedskini.dmsprite}\"\n")
			w.write(f"DMSPRITEINDEX \"{attachedskini.dmspriteindex}\"\n")
			w.write(f"LINKSKINUPDATESTODAGINDEX \"{attachedskini.linkskinupdatestodagindex}\"\n")
		w.write(f"POLYHEDRON\n")
		w.write(f"DEFINITION \"{self.definition}\"\n")
		w.write(f"CENTEROFFSET? \"{self.centeroffset}\"\n")
		w.write(f"BOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"HEXTWOHUNDREDFLAG \"{self.hextwohundredflag}\"\n")
		w.write(f"HEXTWENTYTHOUSANDFLAG \"{self.hextwentythousandflag}\"\n")

