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

	def WriteChannels(self, path):
		with open(path, 'w') as outfile:
			_initCsvDATDialect()
			writer = csv.DictWriter(
				outfile,
				dialect='DAT',
				fieldnames=[
					'id', 'x',  'y', 'inslope', 'inaccel', 'expression',
					'outslope', 'outaccel',
				])
			writer.writeheader()
			# ..........
