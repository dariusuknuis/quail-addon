# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

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

	class xyz:
		xyz:tuple[float, float, float]

	xyzs:list[xyz]

	class xyz:
		xyz:tuple[float, float, float]

	xyzs:list[xyz]

	class wall:

		normalabcd:tuple[float, float, float, float]


		class xyz:
			xyz:tuple[float, float, float]

		xyzs:list[xyz]

	walls:list[wall]

	class obstacle:

		normalabcd:tuple[float, float, float, float]


		class xyz:
			xyz:tuple[float, float, float]

		xyzs:list[xyz]

	obstacles:list[obstacle]

	class cuttingobstacle:

		normalabcd:tuple[float, float, float, float]


		class xyz:
			xyz:tuple[float, float, float]

		xyzs:list[xyz]

	cuttingobstacles:list[cuttingobstacle]

	class visnode:

		normalabcd:tuple[float, float, float, float]

		vislistindex:int

		fronttree:int

		backtree:int

	visnodes:list[visnode]

	class vislist:

		regions:list[str]

	vislists:list[vislist]
	sphere:tuple[float, float, float, float]
	userdata:str
	sprite:str

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "REVERBVOLUME", 1)
		self.reverbvolume = float(records[1])
		records = parse.property(r, "REVERBOFFSET", 1)
		self.reverboffset = int(records[1])
		records = parse.property(r, "REGIONFOG", 1)
		self.regionfog = int(records[1])
		records = parse.property(r, "GOURAND2", 1)
		self.gourand2 = int(records[1])
		records = parse.property(r, "ENCODEDVISIBILITY", 1)
		self.encodedvisibility = int(records[1])
		records = parse.property(r, "VISLISTBYTES", 1)
		self.vislistbytes = int(records[1])
		records = parse.property(r, "NUMREGIONVERTEX", 1)
		numregionvertex = int(records[1])

		self.xyzs = []
		for i in range(numregionvertex):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMRENDERVERTICES", 1)
		numrendervertices = int(records[1])

		self.xyzs = []
		for i in range(numrendervertices):
			xyzi = self.xyz()
			records = parse.property(r, "XYZ", 3)
			xyzi.xyz = float(records[1]), float(records[2]), float(records[3])
			self.xyzs.append(xyzi)
		records = parse.property(r, "NUMWALLS", 1)
		numwalls = int(records[1])

		self.walls = []
		for i in range(numwalls):
			walli = self.wall()
			parse.property(r, "WALL", 0)

			records = parse.property(r, "NORMALABCD", 4)
			walli.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = parse.property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			walli.xyzs = []
			for j in range(numvertices):
				xyzj = self.wall.xyz()
				records = parse.property(r, "XYZ", 3)
				xyzj.xyz = float(records[1]), float(records[2]), float(records[3])
				walli.xyzs.append(xyzj)
			self.walls.append(walli)
		records = parse.property(r, "NUMOBSTACLES", 1)
		numobstacles = int(records[1])

		self.obstacles = []
		for i in range(numobstacles):
			obstaclei = self.obstacle()
			parse.property(r, "OBSTACLE", 0)

			records = parse.property(r, "NORMALABCD", 4)
			obstaclei.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = parse.property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			obstaclei.xyzs = []
			for j in range(numvertices):
				xyzj = self.obstacle.xyz()
				records = parse.property(r, "XYZ", 3)
				xyzj.xyz = float(records[1]), float(records[2]), float(records[3])
				obstaclei.xyzs.append(xyzj)
			self.obstacles.append(obstaclei)
		records = parse.property(r, "NUMCUTTINGOBSTACLES", 1)
		numcuttingobstacles = int(records[1])

		self.cuttingobstacles = []
		for i in range(numcuttingobstacles):
			cuttingobstaclei = self.cuttingobstacle()
			parse.property(r, "CUTTINGOBSTACLE", 0)

			records = parse.property(r, "NORMALABCD", 4)
			cuttingobstaclei.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = parse.property(r, "NUMVERTICES", 1)
			numvertices = int(records[1])

			cuttingobstaclei.xyzs = []
			for j in range(numvertices):
				xyzj = self.cuttingobstacle.xyz()
				records = parse.property(r, "XYZ", 3)
				xyzj.xyz = float(records[1]), float(records[2]), float(records[3])
				cuttingobstaclei.xyzs.append(xyzj)
			self.cuttingobstacles.append(cuttingobstaclei)
		parse.property(r, "VISTREE", 0)

		records = parse.property(r, "NUMVISNODE", 1)
		numvisnode = int(records[1])

		self.visnodes = []
		for i in range(numvisnode):
			visnodei = self.visnode()
			parse.property(r, "VISNODE", 0)

			records = parse.property(r, "NORMALABCD", 4)
			visnodei.normalabcd = float(records[1]), float(records[2]), float(records[3]), float(records[4])
			records = parse.property(r, "VISLISTINDEX", 1)
			visnodei.vislistindex = int(records[1])
			records = parse.property(r, "FRONTTREE", 1)
			visnodei.fronttree = int(records[1])
			records = parse.property(r, "BACKTREE", 1)
			visnodei.backtree = int(records[1])
			self.visnodes.append(visnodei)
		records = parse.property(r, "NUMVISIBLELIST", 1)
		numvisiblelist = int(records[1])

		self.vislists = []
		for i in range(numvisiblelist):
			vislisti = self.vislist()
			parse.property(r, "VISLIST", 0)

			records = parse.property(r, "REGIONS", -1)
			vislisti.regions = records[1:]

			self.vislists.append(vislisti)
		records = parse.property(r, "SPHERE", 4)
		self.sphere = float(records[1]), float(records[2]), float(records[3]), float(records[4])
		records = parse.property(r, "USERDATA", 1)
		self.userdata = str(records[1])
		records = parse.property(r, "SPRITE", 1)
		self.sprite = str(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"REVERBVOLUME \"{self.reverbvolume}\"\n")
		w.write(f"REVERBOFFSET \"{self.reverboffset}\"\n")
		w.write(f"REGIONFOG \"{self.regionfog}\"\n")
		w.write(f"GOURAND2 \"{self.gourand2}\"\n")
		w.write(f"ENCODEDVISIBILITY \"{self.encodedvisibility}\"\n")
		w.write(f"VISLISTBYTES \"{self.vislistbytes}\"\n")
		w.write(f"NUMREGIONVERTEX \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMRENDERVERTICES \"{len(self.xyzs)}\"\n")
		for xyzi in self.xyzs:
			w.write(f"XYZ \"{xyzi.xyz}\"\n")
		w.write(f"NUMWALLS \"{len(self.walls)}\"\n")
		for walli in self.walls:
			w.write(f"WALL\n")
			w.write(f"NORMALABCD \"{walli.normalabcd}\"\n")
			w.write(f"NUMVERTICES \"{len(walli.xyzs)}\"\n")
			for xyzj in walli.xyzs:
				w.write(f"XYZ \"{xyzj.xyz}\"\n")
		w.write(f"NUMOBSTACLES \"{len(self.obstacles)}\"\n")
		for obstaclei in self.obstacles:
			w.write(f"OBSTACLE\n")
			w.write(f"NORMALABCD \"{obstaclei.normalabcd}\"\n")
			w.write(f"NUMVERTICES \"{len(obstaclei.xyzs)}\"\n")
			for xyzj in obstaclei.xyzs:
				w.write(f"XYZ \"{xyzj.xyz}\"\n")
		w.write(f"NUMCUTTINGOBSTACLES \"{len(self.cuttingobstacles)}\"\n")
		for cuttingobstaclei in self.cuttingobstacles:
			w.write(f"CUTTINGOBSTACLE\n")
			w.write(f"NORMALABCD \"{cuttingobstaclei.normalabcd}\"\n")
			w.write(f"NUMVERTICES \"{len(cuttingobstaclei.xyzs)}\"\n")
			for xyzj in cuttingobstaclei.xyzs:
				w.write(f"XYZ \"{xyzj.xyz}\"\n")
		w.write(f"VISTREE\n")
		w.write(f"NUMVISNODE \"{len(self.visnodes)}\"\n")
		for visnodei in self.visnodes:
			w.write(f"VISNODE\n")
			w.write(f"NORMALABCD \"{visnodei.normalabcd}\"\n")
			w.write(f"VISLISTINDEX \"{visnodei.vislistindex}\"\n")
			w.write(f"FRONTTREE \"{visnodei.fronttree}\"\n")
			w.write(f"BACKTREE \"{visnodei.backtree}\"\n")
		w.write(f"NUMVISIBLELIST \"{len(self.vislists)}\"\n")
		for vislisti in self.vislists:
			w.write(f"VISLIST\n")
			w.write(f"REGIONS \"{vislisti.regions}\"\n")
		w.write(f"SPHERE \"{self.sphere}\"\n")
		w.write(f"USERDATA \"{self.userdata}\"\n")
		w.write(f"SPRITE \"{self.sprite}\"\n")

