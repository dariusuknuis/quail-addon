# Generated from quail, DO NOT EDIT
import io
import wce.parse as parse

class rgbdeformationtrackdef:
	@staticmethod
	def definition():
		return "RGBDEFORMATIONTRACKDEF"

	tag:str
	data1:int
	data2:int
	sleep:int
	data4:int

	class rgba:
		rgba:tuple[int, int, int, int]

	rgbas:list[rgba]

	def __init__(self, tag:str, r:io.TextIOWrapper):
		self.tag = tag
		records = parse.property(r, "DATA1", 1)
		self.data1 = int(records[1])
		records = parse.property(r, "DATA2", 1)
		self.data2 = int(records[1])
		records = parse.property(r, "SLEEP", 1)
		self.sleep = int(records[1])
		records = parse.property(r, "DATA4", 1)
		self.data4 = int(records[1])
		parse.property(r, "RGBDEFORMATIONFRAME", 0)

		records = parse.property(r, "NUMRGBAS", 1)
		numrgbas = int(records[1])

		self.rgbas = []
		for i in range(numrgbas):
			rgbai = self.rgba()
			records = parse.property(r, "RGBA", 4)
			rgbai.rgba = int(records[1]), int(records[2]), int(records[3]), int(records[4])
			self.rgbas.append(rgbai)

	def write(self, w:io.TextIOWrapper):
		w.write(f"DATA1 \"{self.data1}\"\n")
		w.write(f"DATA2 \"{self.data2}\"\n")
		w.write(f"SLEEP \"{self.sleep}\"\n")
		w.write(f"DATA4 \"{self.data4}\"\n")
		w.write(f"RGBDEFORMATIONFRAME\n")
		w.write(f"NUMRGBAS \"{len(self.rgbas)}\"\n")
		for rgbai in self.rgbas:
			w.write(f"RGBA \"{rgbai.rgba}\"\n")

