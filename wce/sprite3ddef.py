# Generated from quail, DO NOT EDIT
import io
from .parse import property

class sprite3ddef:
	@staticmethod
	def definition():
		return "SPRITE3DDEF"

	tag:str
	enablegouraud2:int
	centeroffset:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boundingradius:tuple[float, None]

	def __init__(self):
		self.tag = ""
		self.enablegouraud2 = 0 #2
		self.centeroffset = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.boundingradius = tuple[float, None] #2
		self.vertices = []
		self.bspnodes = []
		self.spherelist = self.spherelist()

	class xyz:
		xyz:tuple[float, float, float]

		def __init__(self):
			self.xyz = tuple[float, float, float] #3

	class bspnode:
		normalabcd:tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None]]
		vertexlist:list[str]
		rendermethod:str
		fronttree:int
		backtree:int

		def __init__(self):
			self.normalabcd = tuple[tuple[float, None], tuple[float, None], tuple[float, None], tuple[float, None]] #3
			self.vertexlist = list[str] #3
			self.rendermethod = "" #3
			self.fronttree = 0 #3
			self.backtree = 0 #3
			self.renderinfo = self.renderinfo()

		class renderinfo:
			pen:tuple[int, None]
			brightness:tuple[float, None]
			scaledambient:tuple[float, None]
			uvorigin:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
			uaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
			vaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
			twosided:int

			def __init__(self):
				self.pen = tuple[int, None] #4
				self.brightness = tuple[float, None] #4
				self.scaledambient = tuple[float, None] #4
				self.uvorigin = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #4
				self.uaxis = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #4
				self.vaxis = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #4
				self.twosided = 0 #4
				self.simplespriteinst = self.simplespriteinst()
				self.uvs = []

			class simplespriteinst:
				simplespritetag:tuple[str, None]
				simplespritetagindex:int
				simplespritehaveskipframes:int
				simplespriteskipframes:int

				def __init__(self):
					self.simplespritetag = tuple[str, None] #5
					self.simplespritetagindex = 0 #5
					self.simplespritehaveskipframes = 0 #5
					self.simplespriteskipframes = 0 #5

			class uv:
				uv:tuple[float, float]

				def __init__(self):
					self.uv = tuple[float, float] #5

	class spherelist:
		definition:str
		scalefactor:tuple[float, None]

		def __init__(self):
			self.definition = "" #3
			self.scalefactor = tuple[float, None] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "ENABLEGOURAUD2", 1)
		self.enablegouraud2 = int(records[1])
		records = property(r, "CENTEROFFSET?", 3)
		self.centeroffset = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			xyzi = type(self).xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.vertices.append(xyzi)
		records = property(r, "NUMBSPNODES", 1)
		numbspnodes = int(records[1])

		self.bspnodes = []
		for i in range(numbspnodes):
			bspnodei = type(self).bspnode()
			property(r, "BSPNODE", 0)

			records = property(r, "NORMALABCD?", 4)
			bspnodei.normalabcd = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None), (float(records[4]) if records[4] != "NULL" else None)
			records = property(r, "VERTEXLIST", -1)
			bspnodei.vertexlist = records[1:]

			records = property(r, "RENDERMETHOD", 1)
			bspnodei.rendermethod = str(records[1])
			property(r, "RENDERINFO", 0)

			records = property(r, "PEN?", 1)
			self.renderinfo.pen = (int(records[1]) if records[1] != "NULL" else None)
			records = property(r, "BRIGHTNESS?", 1)
			self.renderinfo.brightness = (float(records[1]) if records[1] != "NULL" else None)
			records = property(r, "SCALEDAMBIENT?", 1)
			self.renderinfo.scaledambient = (float(records[1]) if records[1] != "NULL" else None)
			property(r, "SIMPLESPRITEINST", 0)

			records = property(r, "SIMPLESPRITETAG?", 1)
			self.simplespriteinst.simplespritetag = (str(records[1]) if records[1] != "NULL" else None)
			records = property(r, "SIMPLESPRITETAGINDEX", 1)
			self.simplespriteinst.simplespritetagindex = int(records[1])
			records = property(r, "SIMPLESPRITEHAVESKIPFRAMES", 1)
			self.simplespriteinst.simplespritehaveskipframes = int(records[1])
			records = property(r, "SIMPLESPRITESKIPFRAMES", 1)
			self.simplespriteinst.simplespriteskipframes = int(records[1])
			records = property(r, "UVORIGIN?", 3)
			self.renderinfo.uvorigin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
			records = property(r, "UAXIS?", 3)
			self.renderinfo.uaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
			records = property(r, "VAXIS?", 3)
			self.renderinfo.vaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
			records = property(r, "NUMUVS?", 1)
			numuvs = int(records[1])

			self.renderinfo.uvs = []
			for j in range(numuvs):
				uvj = type(renderinfo).uv()
				records = property(r, "UV", 2)
				uvj.uv = float(records[1]), float(records[2])
				self.renderinfo.uvs.append(uvj)
			records = property(r, "TWOSIDED", 1)
			self.renderinfo.twosided = int(records[1])
			records = property(r, "FRONTTREE", 1)
			bspnodei.fronttree = int(records[1])
			records = property(r, "BACKTREE", 1)
			bspnodei.backtree = int(records[1])
			self.bspnodes.append(bspnodei)
		property(r, "SPHERELIST", 0)

		records = property(r, "DEFINITION", 1)
		self.spherelist.definition = str(records[1])
		records = property(r, "SCALEFACTOR?", 1)
		self.spherelist.scalefactor = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tENABLEGOURAUD2 \"{self.enablegouraud2}\"\n")
		w.write(f"\tCENTEROFFSET? \"{self.centeroffset}\"\n")
		w.write(f"\tNUMVERTICES \"{len(self.vertices)}\"\n")
		for xyzi in self.vertices:
			w.write(f"\t\tXYZ \"{xyzi.xyz}\"\n")
		w.write(f"\tNUMBSPNODES \"{len(self.bspnodes)}\"\n")
		for bspnodei in self.bspnodes:
			w.write(f"\t\tBSPNODE\n")
			w.write(f"\t\tNORMALABCD? \"{bspnodei.normalabcd}\"\n")
			w.write(f"VERTEXLIST \"{bspnodei.vertexlist}\"\n")
			w.write(f"\t\tRENDERMETHOD \"{bspnodei.rendermethod}\"\n")
			w.write(f"\t\tRENDERINFO\n")
			w.write(f"\t\tPEN? \"{self.renderinfo.pen}\"\n")
			w.write(f"\t\tBRIGHTNESS? \"{self.renderinfo.brightness}\"\n")
			w.write(f"\t\tSCALEDAMBIENT? \"{self.renderinfo.scaledambient}\"\n")
			w.write(f"\t\tSIMPLESPRITEINST\n")
			w.write(f"\t\tSIMPLESPRITETAG? \"{self.simplespriteinst.simplespritetag}\"\n")
			w.write(f"\t\tSIMPLESPRITETAGINDEX \"{self.simplespriteinst.simplespritetagindex}\"\n")
			w.write(f"\t\tSIMPLESPRITEHAVESKIPFRAMES \"{self.simplespriteinst.simplespritehaveskipframes}\"\n")
			w.write(f"\t\tSIMPLESPRITESKIPFRAMES \"{self.simplespriteinst.simplespriteskipframes}\"\n")
			w.write(f"\t\tUVORIGIN? \"{self.renderinfo.uvorigin}\"\n")
			w.write(f"\t\tUAXIS? \"{self.renderinfo.uaxis}\"\n")
			w.write(f"\t\tVAXIS? \"{self.renderinfo.vaxis}\"\n")
			w.write(f"\t\tNUMUVS? \"{len(self.renderinfo.uvs)}\"\n")
			for uvj in self.renderinfo.uvs:
				w.write(f"\t\t\tUV \"{uvj.uv}\"\n")
			w.write(f"\t\tTWOSIDED \"{self.renderinfo.twosided}\"\n")
			w.write(f"\t\tFRONTTREE \"{bspnodei.fronttree}\"\n")
			w.write(f"\t\tBACKTREE \"{bspnodei.backtree}\"\n")
		w.write(f"\tSPHERELIST\n")
		w.write(f"\tDEFINITION \"{self.spherelist.definition}\"\n")
		w.write(f"\tSCALEFACTOR? \"{self.spherelist.scalefactor}\"\n")
		w.write(f"\tBOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		return ""

