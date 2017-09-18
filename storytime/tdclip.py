from typing import TextIO, List

class TDClipTrack:
	def __init__(self, name, vals: List[float]):
		self.name = name
		self.vals = vals

	def WriteTo(self, out):
		out.write('    {\n')
		out.write('        name = {}\n'.format(self.name))
		out.write('        data_rle = ')
		# prev = None
		# dupcount = 0
		for val in self.vals:
			out.write('{:.4f} '.format(val))
		out.write('\n')
		out.write('    }\n')

	def __repr__(self):
		return 'TDClipTrack(name={}, vals={})'.format(self.name, self.vals)

class TDClip:
	def __init__(self, rate=None, start=None, length=None):
		self.rate = rate or 60
		self.start = start or 0
		self.length = length or 0
		self.tracks = []  # type: List[TDClipTrack]

	def AddTrack(self, name, vals: List[float]):
		self.tracks.append(TDClipTrack(name, vals))
		if len(vals) > self.length:
			self.length = len(vals)

	def WriteTo(self, out: TextIO):
		out.write('{\n')
		out.write('    rate = {}\n'.format(self.length))
		out.write('    start = {}\n'.format(self.start))
		out.write('    tracklength = {}\n'.format(self.length))
		out.write('    tracks = {}\n'.format(len(self.tracks)))
		for track in self.tracks:
			track.WriteTo(out)
		out.write('    }\n')

	def WriteToFile(self, path):
		with open(path, 'w') as outfile:
			self.WriteTo(outfile)

	def __repr__(self):
		return 'TDClip(rate={}, start={}, length={}, tracks={})'.format(
			self.rate, self.start, self.length, self.tracks)
