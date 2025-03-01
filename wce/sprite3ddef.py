# Generated from quail, DO NOT EDIT
import io
from .parse import property

class sprite3ddef:
	@staticmethod
	def definition():
		return "SPRITE3DDEF"

	tag:str
	centeroffset:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boundingradius:tuple[float, None]
	spherelist:str

	class xyz:
		xyz:tuple[float, float, float]

	xyzs:list[xyz]

	class bspnode:

		vertexlist:list[str]

	bspnodes:list[bspnode]
	rendermethod:str
	pen:tuple[int, None]
	brightness:tuple[float, None]
	scaledambient:tuple[float, None]
	sprite:tuple[str, None]
	uvorigin:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	uaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	vaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]

	class uv:
		uv:tuple[float, float]

	uvs:list[uv]
	twosided:int
	fronttree:int
	backtree:int

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = property(r, "CENTEROFFSET?", 3)
		self.centeroffset = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SPHERELIST", 1)
		self.spherelist = str(records[1])
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.xyzs = []
		for i in range(numvertices):
			xyzi = self.xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = property(r, "NUMBSPNODES", 1)
		numbspnodes = int(records[1])

		self.bspnodes = []
		for i in range(numbspnodes):
			bspnodei = self.bspnode()
			property(r, "BSPNODE", 0)

			records = property(r, "VERTEXLIST", -1)
			bspnodei.vertexlist = records[1:]

			self.bspnodes.append(bspnodei)
		records = property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		property(r, "RENDERINFO", 0)

		records = property(r, "PEN?", 1)
		self.pen = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "BRIGHTNESS?", 1)
		self.brightness = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SCALEDAMBIENT?", 1)
		self.scaledambient = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SPRITE?", 1)
		self.sprite = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "UVORIGIN?", 3)
		self.uvorigin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "UAXIS?", 3)
		self.uaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "VAXIS?", 3)
		self.vaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "UVCOUNT", 1)
		uvcount = int(records[1])

		self.uvs = []
		for i in range(uvcount):
			uvi = self.uv()
			records = property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.uvs.append(uvi)
		records = property(r, "TWOSIDED", 1)
		self.twosided = int(records[1])
		records = property(r, "FRONTTREE", 1)
		self.fronttree = int(records[1])
		records = property(r, "BACKTREE", 1)
		self.backtree = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tCENTEROFFSET? \"{self.centeroffset}\"\n")
		w.write(f"\tBOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"\tSPHERELIST \"{self.spherelist}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"\t\tXYZ \"{xyzi.xyz}\"\n")
		w.write(f"\tNUMBSPNODES \"{len(self.bspnodes)}\"\n")
		for bspnodei in self.bspnodes:
			w.write(f"\t\tBSPNODE\n")
			w.write(f"VERTEXLIST \"{bspnodei.vertexlist}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tRENDERINFO\n")
		w.write(f"\tPEN? \"{self.pen}\"\n")
		w.write(f"\tBRIGHTNESS? \"{self.brightness}\"\n")
		w.write(f"\tSCALEDAMBIENT? \"{self.scaledambient}\"\n")
		w.write(f"\tSPRITE? \"{self.sprite}\"\n")
		w.write(f"\tUVORIGIN? \"{self.uvorigin}\"\n")
		w.write(f"\tUAXIS? \"{self.uaxis}\"\n")
		w.write(f"\tVAXIS? \"{self.vaxis}\"\n")
		w.write(f"\tUVCOUNT \"{len(self.uvs)}\"\n")
		for uvi in self.uvs:
			w.write(f"\t\tUV \"{uvi.uv}\"\n")
		w.write(f"\tTWOSIDED \"{self.twosided}\"\n")
		w.write(f"\tFRONTTREE \"{self.fronttree}\"\n")
		w.write(f"\tBACKTREE \"{self.backtree}\"\n")

