# Generated from quail, DO NOT EDIT
import io
from .parse import property

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
	rendermethod:str
	hextenflag:int

	def __init__(self):
		self.tag = ""
		self.scale = tuple[float, float] #2
		self.spherelisttag = "" #2
		self.depthscale = tuple[float, None] #2
		self.centeroffset = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #2
		self.boundingradius = tuple[float, None] #2
		self.currentframeref = tuple[int, None] #2
		self.sleep = tuple[int, None] #2
		self.rendermethod = "" #2
		self.hextenflag = 0 #2
		self.pitches = []
		self.renderinfo = self.renderinfo()

	class pitch:
		pitchcap:int
		toporbottomview:int

		def __init__(self):
			self.pitchcap = 0 #3
			self.toporbottomview = 0 #3
			self.headings = []

		class heading:
			headingcap:int

			def __init__(self):
				self.headingcap = 0 #4
				self.frames = []

			class frame:
				frame:str

				def __init__(self):
					self.frame = "" #5
					self.files = []

				class file:
					file:str

					def __init__(self):
						self.file = "" #6

	class renderinfo:
		pen:tuple[int, None]
		brightness:tuple[float, None]
		scaledambient:tuple[float, None]
		sprite:tuple[str, None]
		uvorigin:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
		uaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
		vaxis:tuple[tuple[float, None], tuple[float, None], tuple[float, None]]
		twosided:int

		def __init__(self):
			self.pen = tuple[int, None] #3
			self.brightness = tuple[float, None] #3
			self.scaledambient = tuple[float, None] #3
			self.sprite = tuple[str, None] #3
			self.uvorigin = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #3
			self.uaxis = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #3
			self.vaxis = tuple[tuple[float, None], tuple[float, None], tuple[float, None]] #3
			self.twosided = 0 #3
			self.uvcount = []

		class uv:
			uv:tuple[float, float]

			def __init__(self):
				self.uv = tuple[float, float] #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "SCALE", 2)
		self.scale = float(records[1]), float(records[2])
		records = property(r, "SPHERELISTTAG", 1)
		self.spherelisttag = str(records[1])
		records = property(r, "DEPTHSCALE?", 1)
		self.depthscale = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "CENTEROFFSET?", 3)
		self.centeroffset = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "BOUNDINGRADIUS?", 1)
		self.boundingradius = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "CURRENTFRAMEREF?", 1)
		self.currentframeref = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SLEEP?", 1)
		self.sleep = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "NUMPITCHES", 1)
		numpitches = int(records[1])

		self.pitches = []
		for i in range(numpitches):
			pitchi = type(self).pitch()
			property(r, "PITCH", 0)

			records = property(r, "PITCHCAP", 1)
			pitchi.pitchcap = int(records[1])
			records = property(r, "TOPORBOTTOMVIEW", 1)
			pitchi.toporbottomview = int(records[1])
			records = property(r, "NUMHEADINGS", 1)
			numheadings = int(records[1])

			pitchi.headings = []
			for j in range(numheadings):
				headingj = type(pitchi).heading()
				property(r, "HEADING", 0)

				records = property(r, "HEADINGCAP", 1)
				headingj.headingcap = int(records[1])
				records = property(r, "NUMFRAMES", 1)
				numframes = int(records[1])

				headingj.frames = []
				for k in range(numframes):
					framek = type(headingj).frame()
					records = property(r, "FRAME", 1)
					framek.frame = str(records[1])
					records = property(r, "NUMFILES", 1)
					numfiles = int(records[1])

					framek.files = []
					for l in range(numfiles):
						filel = type(framek).file()
						records = property(r, "FILE", 1)
						filel.file = str(records[1])
						framek.files.append(filel)
					headingj.frames.append(framek)
				pitchi.headings.append(headingj)
			self.pitches.append(pitchi)
		records = property(r, "RENDERMETHOD", 1)
		self.rendermethod = str(records[1])
		property(r, "RENDERINFO", 0)

		records = property(r, "PEN?", 1)
		self.renderinfo.pen = (int(records[1]) if records[1] != "NULL" else None)
		records = property(r, "BRIGHTNESS?", 1)
		self.renderinfo.brightness = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SCALEDAMBIENT?", 1)
		self.renderinfo.scaledambient = (float(records[1]) if records[1] != "NULL" else None)
		records = property(r, "SPRITE?", 1)
		self.renderinfo.sprite = (str(records[1]) if records[1] != "NULL" else None)
		records = property(r, "UVORIGIN?", 3)
		self.renderinfo.uvorigin = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "UAXIS?", 3)
		self.renderinfo.uaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "VAXIS?", 3)
		self.renderinfo.vaxis = (float(records[1]) if records[1] != "NULL" else None), (float(records[2]) if records[2] != "NULL" else None), (float(records[3]) if records[3] != "NULL" else None)
		records = property(r, "UVCOUNT", 1)
		uvcount = int(records[1])

		self.renderinfo.uvcount = []
		for i in range(uvcount):
			uvi = type(self.renderinfo).uv()
			records = property(r, "UV", 2)
			uvi.uv = float(records[1]), float(records[2])
			self.renderinfo.uvcount.append(uvi)
		records = property(r, "TWOSIDED", 1)
		self.renderinfo.twosided = int(records[1])
		records = property(r, "HEXTENFLAG", 1)
		self.hextenflag = int(records[1])
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSCALE \"{self.scale}\"\n")
		w.write(f"\tSPHERELISTTAG \"{self.spherelisttag}\"\n")
		w.write(f"\tDEPTHSCALE? \"{self.depthscale}\"\n")
		w.write(f"\tCENTEROFFSET? \"{self.centeroffset}\"\n")
		w.write(f"\tBOUNDINGRADIUS? \"{self.boundingradius}\"\n")
		w.write(f"\tCURRENTFRAMEREF? \"{self.currentframeref}\"\n")
		w.write(f"\tSLEEP? \"{self.sleep}\"\n")
		w.write(f"\tNUMPITCHES \"{len(self.pitches)}\"\n")
		for pitchi in self.pitches:
			w.write(f"\t\tPITCH\n")
			w.write(f"\t\tPITCHCAP \"{pitchi.pitchcap}\"\n")
			w.write(f"\t\tTOPORBOTTOMVIEW \"{pitchi.toporbottomview}\"\n")
			w.write(f"\t\tNUMHEADINGS \"{len(pitchi.headings)}\"\n")
			for headingj in pitchi.headings:
				w.write(f"\t\t\tHEADING\n")
				w.write(f"\t\t\tHEADINGCAP \"{headingj.headingcap}\"\n")
				w.write(f"\t\t\tNUMFRAMES \"{len(headingj.frames)}\"\n")
				for framek in headingj.frames:
					w.write(f"\t\t\t\tFRAME \"{framek.frame}\"\n")
					w.write(f"\t\t\t\tNUMFILES \"{len(framek.files)}\"\n")
					for filel in framek.files:
						w.write(f"\t\t\t\t\tFILE \"{filel.file}\"\n")
		w.write(f"\tRENDERMETHOD \"{self.rendermethod}\"\n")
		w.write(f"\tRENDERINFO\n")
		w.write(f"\t\tPEN? \"{self.renderinfo.pen}\"\n")
		w.write(f"\t\tBRIGHTNESS? \"{self.renderinfo.brightness}\"\n")
		w.write(f"\t\tSCALEDAMBIENT? \"{self.renderinfo.scaledambient}\"\n")
		w.write(f"\t\tSPRITE? \"{self.renderinfo.sprite}\"\n")
		w.write(f"\t\tUVORIGIN? \"{self.renderinfo.uvorigin}\"\n")
		w.write(f"\t\tUAXIS? \"{self.renderinfo.uaxis}\"\n")
		w.write(f"\t\tVAXIS? \"{self.renderinfo.vaxis}\"\n")
		w.write(f"\t\tUVCOUNT \"{len(self.renderinfo.uvcount)}\"\n")
		for uvi in self.renderinfo.uvcount:
			w.write(f"\t\t\tUV \"{uvi.uv}\"\n")
		w.write(f"\t\tTWOSIDED \"{self.renderinfo.twosided}\"\n")
		w.write(f"\tHEXTENFLAG \"{self.hextenflag}\"\n")
		return ""

