try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

# from itertools import chain, zip_longest, dropwhile, takewhile
#
# def extract_data(lines_of_text, searched_text):
# 	"""Extract data for frames relevant to a certain type of transformation"""
#
# 	searched_text = searched_text.lower()
# 	data_with_headers = takewhile(
# 		lambda line: bool(line),
# 		dropwhile(
# 			lambda line: searched_text in line,
# 			lines_of_text))
# 	return list(data_with_headers)[2:]  # dropping headers
#
#
# def strip_frame(data):
# 	"""Remove the frame number and Z axis from a transformation dataset.
#
# 	Also flatten the whole data into a single list.
# 	"""
#
# 	return list(chain.from_iterable(line.split()[1:3] for line in data))
#
#
# def convert_column(column_data, converting_function):
# 	"""Convert data from AE to Nuke using the supplied function"""
#
# 	return [str(converting_function(line)) for line in column_data]

# class AeKeyframeParser(base.Extension):
# 	def __init__(self, comp):
# 		super().__init__(comp)
#

def ParseKeyframes(indat, channels, keys):
	parser = _Parser(indat)
	parser.Parse()
	parser.WriteTo(channels, keys)

SANITY = 20000

class _Parser:
	def __init__(self, indat):
		self.log = base.IndentedLogger()
		self.indat = indat
		self.row = 0
		self.numRows = indat.numRows
		self.blocks = None
		self.maxFrame = 0

	@property
	def _State(self):
		return ''

	def _LogBegin(self, event):
		self.log.LogBegin('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))

	def _Log(self, event):
		self.log.LogEvent('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))

	def _LogEnd(self, event):
		self.log.LogEnd('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))

	def Parse(self):
		self._LogBegin('Parse()')
		try:
			self.row = 2
			if not self._GoToNextBlankRow(1):
				return
			self.row += 1
			self.blocks = []
			sanity = SANITY
			while self.row < self.numRows:
				self._LogBegin('Parse() - scanning row {}...'.format(self.row))
				try:
					if self.indat[self.row, 0] == 'End of Keyframe Data':
						return
					if sanity == 0:
						raise Exception('INSANITY!!!')
					sanity -= 1
					block = self._ParseNextBlock()
					self.blocks.append(block)
					if not self._GoToNextBlankRow(0):
						break
					if self.indat[self.row, 0] == '':
						self.row += 1
					self.row += 1
				finally:
					self._LogEnd('Parse() - done scanning row {}'.format(self.row))
		finally:
			self._LogEnd('Parse()')

	def _GoToNextBlankRow(self, col):
		self._LogBegin('_GoToNextBlankRow()')
		try:
			self.row += 1
			sanity = SANITY
			while self.row < self.numRows:
				if sanity == 0:
					raise Exception('INSANITY!!!')
				sanity -= 1
				if self.indat[self.row, col] == '':
					return True
				self.row += 1
			return False
		finally:
			self._LogEnd('_GoToNextBlankRow()')

	def _ParseNextBlock(self):
		self._LogBegin('_ParseNextBlock()')
		try:
			indat = self.indat
			group = indat[self.row, 0].val
			components = indat[self.row, 1].val
			param = indat[self.row, 2].val
			blockname = '{}/{}/{}'.format(group, components, param)
			self._Log('_ParseNextBlock() - block name: {}'.format(blockname))
			self.row += 1
			attribs = {
				indat[self.row, i].val: []
				for i in range(2, indat.numCols)
				if indat[self.row, i].val != ''
			}
			self._Log('_ParseNextBlock() - attribs: {}'.format(attribs.keys()))
			self.row += 1
			sanity = SANITY
			while self.row < self.numRows:
				if sanity == 0:
					raise Exception('INSANITY!!!')
				sanity -= 1
				if indat[self.row, 1] == '':
					self._Log('_ParseNextBlock() - found blank row in block. stopping')
					break
				f = int(indat[self.row, 1])
				if f > self.maxFrame:
					self.maxFrame = f
				for i, attr in enumerate(attribs):
					attribs[attr].append([f, float(indat[self.row, i + 2])])
				# self._Log('attribs: {}'.format(attribs))
				self.row += 1
			return {
				'name': blockname,
				'attribs': attribs,
			}
		finally:
			self._LogEnd('_ParseNextBlock()')

	def WriteTo(self, channels, keys):
		self._LogBegin('WriteTo()')
		try:
			channels.clear(keepFirstRow=True)
			keys.clear(keepFirstRow=True)
			for block in self.blocks:
				blockname = block['name']
				for attr, frames in block['attribs'].items():
					chanid = channels.numRows
					channels.appendRow([])
					channels[chanid, 'name'] = _Clean('{}/{}'.format(blockname, attr))
					channels[chanid, 'id'] = chanid
					for f, val in frames:
						i = keys.numRows
						keys.appendRow([])
						keys[i, 'id'] = chanid
						keys[i, 'x'] = f
						keys[i, 'y'] = val
						keys[i, 'expression'] = 'linear()'
		finally:
			self._LogEnd('WriteTo()')

def _Clean(n):
	return tdu.legalName(n)
