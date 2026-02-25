# Generated from quail, DO NOT EDIT
import io
from .parse import property

class rgbdeformationtrackdef:
	@staticmethod
	def definition():
		return "RGBDEFORMATIONTRACKDEF"

	tag:str
	sleep:int
	data4:int
	usealpha:int

	def __init__(self):
		self.tag = ""
		self.sleep = 0 #2
		self.data4 = 0 #2
		self.usealpha = 0 #2
		self.rgbdeformationframes = []

	class numrgbas:

		def __init__(self):
			self.rgbas = []

		class rgba:
			rgba:tuple[int, int, int, int]

			def __init__(self):
				self.rgba = tuple[int, int, int, int] #4

	def read(self, tag:str, r:io.TextIOWrapper|None) -> str:
		self.tag = tag
		if r is None:
			return "no reader provided"

		records = property(r, "SLEEP", 1)
		self.sleep = int(records[1])
		records = property(r, "DATA4", 1)
		self.data4 = int(records[1])
		records = property(r, "USEALPHA", 1)
		self.usealpha = int(records[1])
		records = property(r, "NUMRGBDEFORMATIONFRAMES", 1)
		numrgbdeformationframes = int(records[1])

		self.rgbdeformationframes = []
		for i in range(numrgbdeformationframes):
			numrgbasi = type(self).numrgbas()
			records = property(r, "NUMRGBAS", 1)
			numrgbas = int(records[1])

			numrgbasi.rgbas = []
			for j in range(numrgbas):
				rgbaj = type(numrgbasi).rgba()
				records = property(r, "RGBA", 4)
				rgbaj.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
				numrgbasi.rgbas.append(rgbaj)
			self.rgbdeformationframes.append(numrgbasi)
		return ""

	def write(self, w:io.TextIOWrapper)->str:
		w.write(f"{self.definition()} \"{self.tag}\"\n")
		w.write(f"\tSLEEP \"{self.sleep}\"\n")
		w.write(f"\tDATA4 \"{self.data4}\"\n")
		w.write(f"\tUSEALPHA \"{self.usealpha}\"\n")
		w.write(f"\tNUMRGBDEFORMATIONFRAMES \"{len(self.rgbdeformationframes)}\"\n")
		for numrgbasi in self.rgbdeformationframes:
			w.write(f"\t\tNUMRGBAS \"{len(numrgbasi.rgbas)}\"\n")
			for rgbaj in numrgbasi.rgbas:
				w.write(f"\t\t\tRGBA \"{rgbaj.rgba}\"\n")
		return ""

