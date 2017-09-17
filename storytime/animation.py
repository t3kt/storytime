import csv


def _initCsvDATDialect():
	if 'DAT' not in csv.list_dialects():
		csv.register_dialect(
			'DAT',
			delimiter='\t',
			doublequote=False,
			escapechar=None,
			lineterminator='\n',
			quoting=csv.QUOTE_NONE)

def WriteChannels(path, channels):
		with open(path, 'w') as outfile:
			_initCsvDATDialect()
			writer = csv.DictWriter(
				outfile,
				dialect='DAT',
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
		_initCsvDATDialect()
		self.writer = csv.DictWriter(
			self.outfile,
			dialect='DAT',
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
