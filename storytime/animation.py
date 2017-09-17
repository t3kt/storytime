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


class AnimationTableWriter:
	def __init__(self):
		self.channels = []

	def AddChannels(self, channels):
		self.channels += channels

	def WriteChannels(self, path):
		with open(path, 'w') as outfile:
			_initCsvDATDialect()
			writer = csv.DictWriter(
				outfile,
				dialect='DAT',
				fieldnames=[
					'name', 'id',  'left', 'right', 'default', 'keys',
					'liner', 'lineg', 'lineb', 'picked', 'display', 'template',
				])
			pass
