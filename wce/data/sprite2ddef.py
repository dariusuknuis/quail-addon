# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class sprite2ddef:
	@staticmethod
	def definition():
		return "SPRITE2DDEF"

	tag:str
	scale:tuple[float, float]
	spherelisttag:str
	depthscale:tuple[float, None]
	centeroffset:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
	boundingradius:tuple[float, None]
	currentframeref:tuple[int, None]
	sleep:tuple[int, None]

	class pitch:

		pitchcap:int

		toporbottomview:int


		class heading:

			headingcap:int


			class frame:
				frame:str


				class file:
					file:str

				files:list[file]

			frames:list[frame]

		headings:list[heading]

	pitchs:list[pitch]
	rendermethod:str
	pen:tuple[str, None]
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
	hextenflag:int

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "SCALE", 2)
		self.scale = float(records[1]), float(records[2])
		records = parse.property(r, "SPHERELISTTAG", 1)
		self.spherelisttag = str(records[1])
		records = parse.property(r, "DEPTHSCALE?", 1)
		self.depthscale = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "CENTEROFFSET?", 3)
		self.centeroffset = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "CURRENTFRAMEREF?", 1)
		self.currentframeref = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "NUMPITCHES", 1)
		numpitches = int(records[1])

		self.pitchs = []
		for i in range(numpitches):
			pitchi = self.pitch()
			parse.property(r, "PITCH", 0)

			records = parse.property(r, "PITCHCAP", 1)
			pitchi.pitchcap = int(records[1])
			records = parse.property(r, "TOPORBOTTOMVIEW", 1)
			pitchi.toporbottomview = int(records[1])
			records = parse.property(r, "NUMHEADINGS", 1)
			numheadings = int(records[1])

			pitchi.headings = []
			for j in range(numheadings):
				headingj = self.pitch.heading()
				parse.property(r, "HEADING", 0)

				records = parse.property(r, "HEADINGCAP", 1)
				headingj.headingcap = int(records[1])
				records = parse.property(r, "NUMFRAMES", 1)
				numframes = int(records[1])

				headingj.frames = []
				for k in range(numframes):
					framek = self.pitch.heading.frame()
					records = parse.property(r, "FRAME", 1)
					framek.frame = str(records[1])
					records = parse.property(r, "NUMFILES", 1)
					numfiles = int(records[1])

					framek.files = []
					for l in range(numfiles):
						filel = self.pitch.heading.frame.file()
						records = parse.property(r, "FILE", 1)
						filel.file = str(records[1])
						framek.files.append(filel)
					headingj.frames.append(framek)
				pitchi.headings.append(headingj)
			self.pitchs.append(pitchi)
		records = parse.property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		parse.property(r, "RENDERINFO", 0)

		records = parse.property(r, "PEN?", 1)
		self.pen = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "BRIGHTNESS?", 1)
		self.brightness = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SCALEDAMBIENT?", 1)
		self.scaledambient = (float(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "SPRITE?", 1)
		self.sprite = (str(records[1]) if records[1] != "NULL" else None)
		records = parse.property(r, "UVORIGIN?", 3)
		self.uvorigin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "UAXIS?", 3)
		self.uaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "VAXIS?", 3)
		self.vaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = parse.property(r, "UVCOUNT", 1)
		uvcount = int(records[1])

		self.uvs = []
		for i in range(uvcount):
			uvi = self.uv()
			records = parse.property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.uvs.append(uvi)
		records = parse.property(r, "TWOSIDED", 1)
		self.twosided = int(records[1])
		records = parse.property(r, "HEXTENFLAG", 1)
		self.hextenflag = int(records[1])

	def write(self, w:io.TextIOWrapper):
		w.write(f"SCALE \"{self.scale}\"\n")
		w.write(f"SPHERELISTTAG \"{self.spherelisttag}\"\n")
		w.write(f"DEPTHSCALE? \"{self.depthscale}\"\n")
		w.write(f"CENTEROFFSET? \"{self.centeroffset}\"\n")
		w.write(f"BOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"CURRENTFRAMEREF? \"{self.currentframeref}\"\n")
		w.write(f"SLEEP? \"{self.sleep}\"\n")
		w.write(f"NUMPITCHES \"{len(self.pitchs)}\"\n")
		for pitchi in self.pitchs:
			w.write(f"PITCH\n")
			w.write(f"PITCHCAP \"{pitchi.pitchcap}\"\n")
			w.write(f"TOPORBOTTOMVIEW \"{pitchi.toporbottomview}\"\n")
			w.write(f"NUMHEADINGS \"{len(pitchi.headings)}\"\n")
			for headingj in pitchi.headings:
				w.write(f"HEADING\n")
				w.write(f"HEADINGCAP \"{headingj.headingcap}\"\n")
				w.write(f"NUMFRAMES \"{len(headingj.frames)}\"\n")
				for framek in headingj.frames:
					w.write(f"FRAME \"{framek.frame}\"\n")
					w.write(f"NUMFILES \"{len(framek.files)}\"\n")
					for filel in framek.files:
						w.write(f"FILE \"{filel.file}\"\n")
		w.write(f"RENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"RENDERINFO\n")
		w.write(f"PEN? \"{self.pen}\"\n")
		w.write(f"BRIGHTNESS? \"{self.brightness}\"\n")
		w.write(f"SCALEDAMBIENT? \"{self.scaledambient}\"\n")
		w.write(f"SPRITE? \"{self.sprite}\"\n")
		w.write(f"UVORIGIN? \"{self.uvorigin}\"\n")
		w.write(f"UAXIS? \"{self.uaxis}\"\n")
		w.write(f"VAXIS? \"{self.vaxis}\"\n")
		w.write(f"UVCOUNT \"{len(self.uvs)}\"\n")
		for uvi in self.uvs:
			w.write(f"UV \"{uvi.uv}\"\n")
		w.write(f"TWOSIDED \"{self.twosided}\"\n")
		w.write(f"HEXTENFLAG \"{self.hextenflag}\"\n")

