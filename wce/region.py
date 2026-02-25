# Generated from quail, DO NOT EDIT
import io
from .parse import property

class region:
	@staticmethod
	def definition():
		return "REGION"

	tag:str
	reverbvolume:float
	reverboffset:int
	regionfog:int
	gourand2:int
	encodedvisibility:int
	vislistbytes:int
	sphere:tuple[float, float, float, float]
	userdata:str
	sprite:str

	def __init__(self):
		self.tag = ""
		self.reverbvolume = 0.0 #2
		self.reverboffset = 0 #2
		self.regionfog = 0 #2
		self.gourand2 = 0 #2
		self.encodedvisibility = 0 #2
		self.vislistbytes = 0 #2
		self.sphere = tuple[float, float, float, float] #2
		self.userdata = "" #2
		self.sprite = "" #2
		self.regionvertexs = []
		self.rendervertices = []
		self.walls = []
		self.obstacles = []
		self.cuttingobstacles = []
		self.visnodes = []
		self.visiblelists = []

	class xyz:
		xyz:tuple[float, float, float]

		def __init__(self):
			self.xyz = tuple[float, float, float] #3

	class vxyz:
		vxyz:tuple[float, float, float]

		def __init__(self):
			self.vxyz = tuple[float, float, float] #3

	class wall:
		normalabcd:tuple[float, float, float, float]

		def __init__(self):
			self.normalabcd = tuple[float, float, float, float] #3
			self.vertices = []

		class wxyz:
			wxyz:tuple[float, float, float]

			def __init__(self):
				self.wxyz = tuple[float, float, float] #4

	class obstacle:
		onormalabcd:tuple[float, float, float, float]

		def __init__(self):
			self.onormalabcd = tuple[float, float, float, float] #3
			self.overtices = []

		class oxyz:
			oxyz:tuple[float, float, float]

			def __init__(self):
				self.oxyz = tuple[float, float, float] #4

	class cuttingobstacle:
		cnormalabcd:tuple[float, float, float, float]

		def __init__(self):
			self.cnormalabcd = tuple[float, float, float, float] #3
			self.cvertices = []

		class cxyz:
			cxyz:tuple[float, float, float]

			def __init__(self):
				self.cxyz = tuple[float, float, float] #4

	class visnode:
		vnormalabcd:tuple[float, float, float, float]
		vislistindex:int
		fronttree:int
		backtree:int

		def __init__(self):
			self.vnormalabcd = tuple[float, float, float, float] #3
			self.vislistindex = 0 #3
			self.fronttree = 0 #3
			self.backtree = 0 #3

	class vislist:
		range:list[str]

		def __init__(self):
			self.range = list[str] #3

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "REVERBVOLUME", 1)
		self.reverbvolume = float(records[1])
		records = property(r, "REVERBOFFSET", 1)
		self.reverboffset = int(records[1])
		records = property(r, "REGIONFOG", 1)
		self.regionfog = int(records[1])
		records = property(r, "GOURAND2", 1)
		self.gourand2 = int(records[1])
		records = property(r, "ENCODEDVISIBILITY", 1)
		self.encodedvisibility = int(records[1])
		records = property(r, "VISLISTBYTES", 1)
		self.vislistbytes = int(records[1])
		records = property(r, "NUMREGIONVERTEXS", 1)
		numregionvertexs = int(records[1])

		self.regionvertexs = []
		for i in range(numregionvertexs):
			xyzi = type(self).xyz()
			records = property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.regionvertexs.append(xyzi)
		records = property(r, "NUMRENDERVERTICES", 1)
		numrendervertices = int(records[1])

		self.rendervertices = []
		for i in range(numrendervertices):
			vxyzi = type(self).vxyz()
			records = property(r, "VXYZ", 3)
			vxyzi.vxyz = float(records[1]), float(records[2]), float(records[3])
			self.rendervertices.append(vxyzi)
		records = property(r, "NUMWALLS", 1)
		numwalls = int(records[1])

		self.walls = []
		for i in range(numwalls):
			walli = type(self).wall()
			property(r, "WALL", 0)

			records = property(r, "NORMALABCD", 4)
			walli.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			walli.vertices = []
			for j in range(numvertices):
				wxyzj = type(walli).wxyz()
				records = property(r, "WXYZ", 3)
				wxyzj.wxyz = float(records[1]), float(records[2]), float(records[3])
				walli.vertices.append(wxyzj)
			self.walls.append(walli)
		records = property(r, "NUMOBSTACLES", 1)
		numobstacles = int(records[1])

		self.obstacles = []
		for i in range(numobstacles):
			obstaclei = type(self).obstacle()
			property(r, "OBSTACLE", 0)

			records = property(r, "ONORMALABCD", 4)
			obstaclei.onormalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = property(r, "NUMOVERTICES", 1)
			numovertices = int(records[1])

			obstaclei.overtices = []
			for j in range(numovertices):
				oxyzj = type(obstaclei).oxyz()
				records = property(r, "OXYZ", 3)
				oxyzj.oxyz = float(records[1]), float(records[2]), float(records[3])
				obstaclei.overtices.append(oxyzj)
			self.obstacles.append(obstaclei)
		records = property(r, "NUMCUTTINGOBSTACLES", 1)
		numcuttingobstacles = int(records[1])

		self.cuttingobstacles = []
		for i in range(numcuttingobstacles):
			cuttingobstaclei = type(self).cuttingobstacle()
			property(r, "CUTTINGOBSTACLE", 0)

			records = property(r, "CNORMALABCD", 4)
			cuttingobstaclei.cnormalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = property(r, "NUMCVERTICES", 1)
			numcvertices = int(records[1])

			cuttingobstaclei.cvertices = []
			for j in range(numcvertices):
				cxyzj = type(cuttingobstaclei).cxyz()
				records = property(r, "CXYZ", 3)
				cxyzj.cxyz = float(records[1]), float(records[2]), float(records[3])
				cuttingobstaclei.cvertices.append(cxyzj)
			self.cuttingobstacles.append(cuttingobstaclei)
		property(r, "VISTREE", 0)

		records = property(r, "NUMVISNODES", 1)
		numvisnodes = int(records[1])

		self.visnodes = []
		for i in range(numvisnodes):
			visnodei = type(self).visnode()
			property(r, "VISNODE", 0)

			records = property(r, "VNORMALABCD", 4)
			visnodei.vnormalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = property(r, "VISLISTINDEX", 1)
			visnodei.vislistindex = int(records[1])
			records = property(r, "FRONTTREE", 1)
			visnodei.fronttree = int(records[1])
			records = property(r, "BACKTREE", 1)
			visnodei.backtree = int(records[1])
			self.visnodes.append(visnodei)
		records = property(r, "NUMVISIBLELISTS", 1)
		numvisiblelists = int(records[1])

		self.visiblelists = []
		for i in range(numvisiblelists):
			vislisti = type(self).vislist()
			property(r, "VISLIST", 0)

			records = property(r, "RANGE", -1)
			vislisti.range = records[1:]

			self.visiblelists.append(vislisti)
		records = property(r, "SPHERE", 4)
		self.sphere = float(records[1]), float(records[2]), float(records[3]), float(records[4])
		records = property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		records = property(r, "SPRITE", 1)
		self.sprite = str(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tREVERBVOLUME \"{self.reverbvolume}\"\n")
		w.write(f"\tREVERBOFFSET \"{self.reverboffset}\"\n")
		w.write(f"\tREGIONFOG \"{self.regionfog}\"\n")
		w.write(f"\tGOURAND2 \"{self.gourand2}\"\n")
		w.write(f"\tENCODEDVISIBILITY \"{self.encodedvisibility}\"\n")
		w.write(f"\tVISLISTBYTES \"{self.vislistbytes}\"\n")
		w.write(f"\tNUMREGIONVERTEXS \"{len(self.regionvertexs)}\"\n")
		for xyzi in self.regionvertexs:
			w.write(f"\t\tXYZ \"{xyzi.xyz}\"\n")
		w.write(f"\tNUMRENDERVERTICES \"{len(self.rendervertices)}\"\n")
		for vxyzi in self.rendervertices:
			w.write(f"\t\tVXYZ \"{vxyzi.vxyz}\"\n")
		w.write(f"\tNUMWALLS \"{len(self.walls)}\"\n")
		for walli in self.walls:
			w.write(f"\t\tWALL\n")
			w.write(f"\t\tNORMALABCD \"{walli.normalabcd}\"\n")
			w.write(f"\t\tNUMVERTICES \"{len(walli.vertices)}\"\n")
			for wxyzj in walli.vertices:
				w.write(f"\t\t\tWXYZ \"{wxyzj.wxyz}\"\n")
		w.write(f"\tNUMOBSTACLES \"{len(self.obstacles)}\"\n")
		for obstaclei in self.obstacles:
			w.write(f"\t\tOBSTACLE\n")
			w.write(f"\t\tONORMALABCD \"{obstaclei.onormalabcd}\"\n")
			w.write(f"\t\tNUMOVERTICES \"{len(obstaclei.overtices)}\"\n")
			for oxyzj in obstaclei.overtices:
				w.write(f"\t\t\tOXYZ \"{oxyzj.oxyz}\"\n")
		w.write(f"\tNUMCUTTINGOBSTACLES \"{len(self.cuttingobstacles)}\"\n")
		for cuttingobstaclei in self.cuttingobstacles:
			w.write(f"\t\tCUTTINGOBSTACLE\n")
			w.write(f"\t\tCNORMALABCD \"{cuttingobstaclei.cnormalabcd}\"\n")
			w.write(f"\t\tNUMCVERTICES \"{len(cuttingobstaclei.cvertices)}\"\n")
			for cxyzj in cuttingobstaclei.cvertices:
				w.write(f"\t\t\tCXYZ \"{cxyzj.cxyz}\"\n")
		w.write(f"\tVISTREE\n")
		w.write(f"\tNUMVISNODES \"{len(self.visnodes)}\"\n")
		for visnodei in self.visnodes:
			w.write(f"\t\tVISNODE\n")
			w.write(f"\t\tVNORMALABCD \"{visnodei.vnormalabcd}\"\n")
			w.write(f"\t\tVISLISTINDEX \"{visnodei.vislistindex}\"\n")
			w.write(f"\t\tFRONTTREE \"{visnodei.fronttree}\"\n")
			w.write(f"\t\tBACKTREE \"{visnodei.backtree}\"\n")
		w.write(f"\tNUMVISIBLELISTS \"{len(self.visiblelists)}\"\n")
		for vislisti in self.visiblelists:
			w.write(f"\t\tVISLIST\n")
			w.write(f"RANGE \"{vislisti.range}\"\n")
		w.write(f"\tSPHERE \"{self.sphere}\"\n")
		w.write(f"\tUSERDATA \"{self.userdata}\"\n")
		w.write(f"\tSPRITE \"{self.sprite}\"\n")
		return ""

