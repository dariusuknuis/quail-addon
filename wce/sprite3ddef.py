# Generated from quail, DO NOT EDIT
import io
from .parse import property

class sprite3ddef:
	@staticmethod
	def definition():
		return "SPRITE3DDEF"

	tag:str
	enablegouraud2:int
	centeroffset:tuple[float, float, float] | None
	boundingradius:float | None

	def __init__(self):
		self.tag = ""
		self.enablegouraud2 = 0 #2
		self.centeroffset = None #2
		self.boundingradius = None #2
		self.vertices = []
		self.bspnodes = []
		self.spherelist = self.spherelist()

	class xyz:
		xyz:tuple[float, float, float]

		def __init__(self):
			self.xyz = (0.0, 0.0, 0.0) #3

	class bspnode:

		def __init__(self):
			self.bspnode = self.bspnode()

		class bspnode:
			normalabcd:tuple[float, float, float, float] | None
			vertexlist:list[str]
			rendermethod:str
			fronttree:int
			backtree:int

			def __init__(self):
				self.normalabcd = None #4
				self.vertexlist = [] #4
				self.rendermethod = "" #4
				self.fronttree = 0 #4
				self.backtree = 0 #4
				self.renderinfo = self.renderinfo()

			class renderinfo:
				pen:int | None
				brightness:float | None
				scaledambient:float | None
				uvorigin:tuple[float, float, float] | None
				uaxis:tuple[float, float, float] | None
				vaxis:tuple[float, float, float] | None
				twosided:int

				def __init__(self):
					self.pen = None #5
					self.brightness = None #5
					self.scaledambient = None #5
					self.uvorigin = None #5
					self.uaxis = None #5
					self.vaxis = None #5
					self.twosided = 0 #5
					self.simplespriteinst = self.simplespriteinst()
					self.uvs = []

				class simplespriteinst:
					simplespritetag:str | None
					simplespritehaveskipframes:int
					simplespriteskipframes:int

					def __init__(self):
						self.simplespritetag = None #6
						self.simplespritehaveskipframes = 0 #6
						self.simplespriteskipframes = 0 #6

				class uv:
					uv:tuple[float, float]

					def __init__(self):
						self.uv = (0.0, 0.0) #6

	class spherelist:
		definition:str
		scalefactor:float | None

		def __init__(self):
			self.definition = "" #3
			self.scalefactor = None #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "ENABLEGOURAUD2", 1)
		self.enablegouraud2 = int(records[1])
		records = property(r, "CENTEROFFSET?", 3)
		self.centeroffset = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]))
		records = property(r, "NUMVERTICES", 1)
		numvertices = int(records[1])

		self.vertices = []
		for i in range(numvertices):
			xyzi = type(self).xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = (float(records[1]), float(records[2]), float(records[3]))
			self.vertices.append(xyzi)
		records = property(r, "NUMBSPNODES", 1)
		numbspnodes = int(records[1])

		self.bspnodes = []
		for i in range(numbspnodes):
			bspnodei = type(self).bspnode()
			property(r, "BSPNODE", 0)

			records = property(r, "NORMALABCD?", 4)
			bspnodei.bspnode.normalabcd = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]), float(records[4]))
			records = property(r, "VERTEXLIST", -1)
			bspnodei.bspnode.vertexlist = records[1:]

			records = property(r, "RENDERMETHOD", 1)
			bspnodei.bspnode.rendermethod = str(records[1])
			property(r, "RENDERINFO", 0)

			records = property(r, "PEN?", 1)
			bspnodei.bspnode.renderinfo.pen = int(records[1]) if records[1] != "NULL" else None
			records = property(r, "BRIGHTNESS?", 1)
			bspnodei.bspnode.renderinfo.brightness = float(records[1]) if records[1] != "NULL" else None
			records = property(r, "SCALEDAMBIENT?", 1)
			bspnodei.bspnode.renderinfo.scaledambient = float(records[1]) if records[1] != "NULL" else None
			property(r, "SIMPLESPRITEINST", 0)

			records = property(r, "SIMPLESPRITETAG?", 1)
			bspnodei.bspnode.renderinfo.simplespriteinst.simplespritetag = str(records[1]) if records[1] != "NULL" else None
			records = property(r, "SIMPLESPRITEHAVESKIPFRAMES", 1)
			bspnodei.bspnode.renderinfo.simplespriteinst.simplespritehaveskipframes = int(records[1])
			records = property(r, "SIMPLESPRITESKIPFRAMES", 1)
			bspnodei.bspnode.renderinfo.simplespriteinst.simplespriteskipframes = int(records[1])
			records = property(r, "UVORIGIN?", 3)
			bspnodei.bspnode.renderinfo.uvorigin = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "UAXIS?", 3)
			bspnodei.bspnode.renderinfo.uaxis = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "VAXIS?", 3)
			bspnodei.bspnode.renderinfo.vaxis = None if records[1] == "NULL" else (float(records[1]), float(records[2]), float(records[3]))
			records = property(r, "NUMUVS?", 1)
			numuvs = int(records[1]) if records[1] != "NULL" else None

			bspnodei.bspnode.renderinfo.uvs = []
			for j in range(numuvs or 0):
				uvj = type(bspnodei.bspnode.renderinfo).uv()
				records = property(r, "UV", 2)
				uvj.uv = (float(records[1]), float(records[2]))
				bspnodei.bspnode.renderinfo.uvs.append(uvj)
			records = property(r, "TWOSIDED", 1)
			bspnodei.bspnode.renderinfo.twosided = int(records[1])
			records = property(r, "FRONTTREE", 1)
			bspnodei.bspnode.fronttree = int(records[1])
			records = property(r, "BACKTREE", 1)
			bspnodei.bspnode.backtree = int(records[1])
			self.bspnodes.append(bspnodei)
		property(r, "SPHERELIST", 0)

		records = property(r, "DEFINITION", 1)
		self.spherelist.definition = str(records[1])
		records = property(r, "SCALEFACTOR?", 1)
		self.spherelist.scalefactor = float(records[1]) if records[1] != "NULL" else None
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = float(records[1]) if records[1] != "NULL" else None
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tENABLEGOURAUD2 {self.enablegouraud2}\n")
		w.write(f"\tCENTEROFFSET? {('NULL' if self.centeroffset is None else self.centeroffset[0])} {('NULL' if self.centeroffset is None else self.centeroffset[1])} {('NULL' if self.centeroffset is None else self.centeroffset[2])}\n")
		w.write(f"\tNUMVERTICES \"{len(self.vertices)}\"\n")
		for xyzi in self.vertices:
			w.write(f"\t\tXYZ {xyzi.xyz[0]} {xyzi.xyz[1]} {xyzi.xyz[2]}\n")
		w.write(f"\tNUMBSPNODES \"{len(self.bspnodes)}\"\n")
		for bspnodei in self.bspnodes:
			w.write(f"\t\tBSPNODE\n")
			w.write(f"\t\t\tNORMALABCD? {('NULL' if bspnodei.bspnode.normalabcd is None else bspnodei.bspnode.normalabcd[0])} {('NULL' if bspnodei.bspnode.normalabcd is None else bspnodei.bspnode.normalabcd[1])} {('NULL' if bspnodei.bspnode.normalabcd is None else bspnodei.bspnode.normalabcd[2])} {('NULL' if bspnodei.bspnode.normalabcd is None else bspnodei.bspnode.normalabcd[3])}\n")
			w.write(f"\t\t\tVERTEXLIST {bspnodei.bspnode.vertexlist}\n")
			w.write(f"\t\t\tRENDERMETHOD \"{bspnodei.bspnode.rendermethod}\"\n")
			w.write(f"\t\t\tRENDERINFO\n")
			w.write(f"\t\t\t\tPEN? {('NULL' if bspnodei.bspnode.renderinfo.pen is None else bspnodei.bspnode.renderinfo.pen)}\n")
			w.write(f"\t\t\t\tBRIGHTNESS? {('NULL' if bspnodei.bspnode.renderinfo.brightness is None else bspnodei.bspnode.renderinfo.brightness)}\n")
			w.write(f"\t\t\t\tSCALEDAMBIENT? {('NULL' if bspnodei.bspnode.renderinfo.scaledambient is None else bspnodei.bspnode.renderinfo.scaledambient)}\n")
			w.write(f"\t\t\t\tSIMPLESPRITEINST\n")
			w.write(f"\t\t\t\t\tSIMPLESPRITETAG? \"{bspnodei.bspnode.renderinfo.simplespriteinst.simplespritetag}\"\n")
			w.write(f"\t\t\t\t\tSIMPLESPRITEHAVESKIPFRAMES {bspnodei.bspnode.renderinfo.simplespriteinst.simplespritehaveskipframes}\n")
			w.write(f"\t\t\t\t\tSIMPLESPRITESKIPFRAMES {bspnodei.bspnode.renderinfo.simplespriteinst.simplespriteskipframes}\n")
			w.write(f"\t\t\t\tUVORIGIN? {('NULL' if bspnodei.bspnode.renderinfo.uvorigin is None else bspnodei.bspnode.renderinfo.uvorigin[0])} {('NULL' if bspnodei.bspnode.renderinfo.uvorigin is None else bspnodei.bspnode.renderinfo.uvorigin[1])} {('NULL' if bspnodei.bspnode.renderinfo.uvorigin is None else bspnodei.bspnode.renderinfo.uvorigin[2])}\n")
			w.write(f"\t\t\t\tUAXIS? {('NULL' if bspnodei.bspnode.renderinfo.uaxis is None else bspnodei.bspnode.renderinfo.uaxis[0])} {('NULL' if bspnodei.bspnode.renderinfo.uaxis is None else bspnodei.bspnode.renderinfo.uaxis[1])} {('NULL' if bspnodei.bspnode.renderinfo.uaxis is None else bspnodei.bspnode.renderinfo.uaxis[2])}\n")
			w.write(f"\t\t\t\tVAXIS? {('NULL' if bspnodei.bspnode.renderinfo.vaxis is None else bspnodei.bspnode.renderinfo.vaxis[0])} {('NULL' if bspnodei.bspnode.renderinfo.vaxis is None else bspnodei.bspnode.renderinfo.vaxis[1])} {('NULL' if bspnodei.bspnode.renderinfo.vaxis is None else bspnodei.bspnode.renderinfo.vaxis[2])}\n")
			w.write(f"\t\t\t\tNUMUVS? \"{len(bspnodei.bspnode.renderinfo.uvs)}\"\n")
			for uvj in bspnodei.bspnode.renderinfo.uvs:
				w.write(f"\t\t\t\t\tUV {uvj.uv[0]} {uvj.uv[1]}\n")
			w.write(f"\t\t\t\tTWOSIDED {bspnodei.bspnode.renderinfo.twosided}\n")
			w.write(f"\t\t\tFRONTTREE {bspnodei.bspnode.fronttree}\n")
			w.write(f"\t\t\tBACKTREE {bspnodei.bspnode.backtree}\n")
		w.write(f"\tSPHERELIST\n")
		w.write(f"\t\tDEFINITION \"{self.spherelist.definition}\"\n")
		w.write(f"\t\tSCALEFACTOR? {('NULL' if self.spherelist.scalefactor is None else self.spherelist.scalefactor)}\n")
		w.write(f"\tBOUNDINGRADIUS? {('NULL' if self.boundingradius is None else self.boundingradius)}\n")
		return ""

