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
		cells = self.indat.row(self.row)
		return '       | cells: {0!r}'.format([repr(c.val) for c in cells] if cells else 'None')

	def _LogBegin(self, event):
		self.log.LogBegin('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))

	def _Log(self, event):
		self.log.LogEvent('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))

	def _LogEnd(self, event=None):
		if event:
			self.log.LogEnd('(aekeyparser)', str(self.row), '{} {}'.format(event, self._State))
		else:
			self.log.LogEnd('', '', None)

	def _GoToNextRow(self):
		self.row += 1

	def _LogCurrentRow(self):
		cells = self.indat.row(self.row)
		self._Log('current row : {0!r}'.format([repr(c.val) for c in cells] if cells else 'None'))

	def Parse(self):
		self._LogBegin('Parse()')
		try:
			self._GoToNextRow()
			self._GoToNextRow()
			if not self._GoToNextBlankRow(1):
				return
			self._GoToNextRow()
			self.blocks = []
			sanity = SANITY
			while self.row < self.numRows:
				self._LogBegin('Parse() - scanning row {}...'.format(self.row))
				self._LogCurrentRow()
				try:
					if self.indat[self.row, 0] == 'End of Keyframe Data':
						return
					if sanity == 0:
						raise Exception('INSANITY!!!')
					sanity -= 1
					block = self._ParseNextBlock()
					self.blocks.append(block)
					if self.indat[self.row, 0] == '':
						self._GoToNextRow()
					if self.indat[self.row, 0] == '':
						self._GoToNextRow()
				finally:
					self._LogEnd('Parse() - done scanning row {}'.format(self.row))
		finally:
			self._LogEnd()

	def _GoToNextBlankRow(self, col):
		self._LogBegin('_GoToNextBlankRow()')
		try:
			self._GoToNextRow()
			sanity = SANITY
			while self.row < self.numRows:
				if sanity == 0:
					raise Exception('INSANITY!!!')
				sanity -= 1
				if self.indat[self.row, col] == '':
					return True
				self._GoToNextRow()
			return False
		finally:
			self._LogEnd()

	def _ParseNextBlock(self):
		self._LogBegin('_ParseNextBlock()')
		try:
			indat = self.indat
			group = indat[self.row, 0].val
			components = indat[self.row, 1].val
			param = indat[self.row, 2].val
			blockname = '{}/{}/{}'.format(group, components, param)
			self._Log('_ParseNextBlock() - block name: {}'.format(blockname))
			self._GoToNextRow()
			attribs = {
				indat[self.row, i].val: []
				for i in range(2, indat.numCols)
				if indat[self.row, i].val != ''
			}
			self._Log('_ParseNextBlock() - attribs: {}'.format(attribs.keys()))
			sanity = SANITY
			numframes = 0
			while self.row < self.numRows:
				self._GoToNextRow()
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
				numframes += 1
				# self._Log('attribs: {}'.format(attribs))
			self._Log('_ParseNextBlock() - found {} frames'.format(numframes))
			return {
				'name': blockname,
				'attribs': attribs,
			}
		finally:
			self._LogEnd()

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
					channels[chanid, 'left'] = channels[chanid, 'right'] = 'hold'
					channels[chanid, 'default'] = 0
					channels[chanid, 'keys'] = 'keys'
					channels[chanid, 'liner'] = 0.14
					channels[chanid, 'lineg'] = 0.5
					channels[chanid, 'lineb'] = 0.5
					channels[chanid, 'picked'] = 0
					channels[chanid, 'display'] = 1
					channels[chanid, 'template'] = 0
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
