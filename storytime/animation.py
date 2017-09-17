from storytime.shared import *

def WriteChannels(path, channels):
		with open(path, 'w') as outfile:
			writer = DATDictWriter(
				outfile,
				fieldnames=[
					'name', 'id',  'left', 'right', 'default', 'keys',
					'liner', 'lineg', 'lineb', 'picked', 'display', 'template',
				])
			writer.writeheader()
			i = 1
			for channel in channels:
				writer.writerow({
					'name': channel,
					'id': i,
					'left': 'hold',
					'right': 'hold',
					'default': 0,
					'keys': 'keys',
					'liner': 0.1,
					'lineg': 0.5,
					'lineb': 0.5,
					'picked': 1,
					'display': 1,
					'template': 0,
				})
				i += 1

class AnimationKeysWriter:
	def __init__(self, path, channels):
		self.path = path
		self.channels = channels
		self.outfile = None
		self.writer = None  # type: csv.DictWriter

	def __enter__(self):
		self.outfile = open(self.path, 'w')
		self.writer = DATDictWriter(
			self.outfile,
			fieldnames=[
				'id', 'x',  'y', 'inslope', 'inaccel', 'expression',
				'outslope', 'outaccel',
			])
		return None

	def __exit__(self, exc_type, exc_val, exc_tb):
		result = self.outfile.__exit__(exc_type, exc_val, exc_tb)
		self.outfile = None
		return result

	def WriteHeader(self):
		self.writer.writeheader()

	def WriteFrameFromList(self, frame, channelvals):
		for channelindex, channelval in enumerate(channelvals):
			self.writer.writerow({
				'id': channelindex + 1,
				'x': frame,
				'y': channelval,
				'inslope': '',
				'inaccel': '',
				'expression': 'linear()',
				'outslope': '',
				'outaccel': '',
			})
