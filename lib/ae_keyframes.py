import re

try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

if False:
	from _stubs import *

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

class AeKeyframeParser(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.animation = comp.op('./animation')
		self.datatable = comp.op('./key_data_table')
		self.channels = self.animation.op('./channels')
		self.keys = self.animation.op('./keys')
		self.Keyframes = KeyframeSet()
		self.LoadKeyframes()

	def LoadKeyframes(self):
		self.datatable.par.loadonstart.pulse()
		self.channels.clear(keepFirstRow=True)
		self.keys.clear(keepFirstRow=True)

		parser = _Parser(
			self,
			self.datatable,
			verbose=self.comp.par.Verbose.eval())
		parser.Parse()
		self.Keyframes = parser.output
		self._WriteKeyframes()

	def _WriteKeyframes(self):
		self._LogBegin('_WriteKeyframes()')
		try:
			self.animation.par.end = self.Keyframes.maxframe
			channels = self.channels
			keys = self.keys
			channels.clear(keepFirstRow=True)
			keys.clear(keepFirstRow=True)
			for block in self.Keyframes.blocks:
				blockname = _Clean(block.name)
				for attr, frames in block.attrs.items():
					chanid = channels.numRows
					channels.appendRow([])
					channels[chanid, 'name'] = '{}:{}'.format(blockname, _Clean(attr))
					channels[chanid, 'id'] = chanid
					channels[chanid, 'left'] = channels[chanid, 'right'] = 'hold'
					channels[chanid, 'default'] = 0
					channels[chanid, 'keys'] = 'keys'
					channels[chanid, 'liner'] = 0.14
					channels[chanid, 'lineg'] = 0.5
					channels[chanid, 'lineb'] = 0.5
					channels[chanid, 'picked'] = 1
					channels[chanid, 'display'] = 1
					channels[chanid, 'template'] = 0
					for f, val in frames:
						i = keys.numRows
						keys.appendRow([])
						keys[i, 'id'] = chanid
						keys[i, 'x'] = f + 1
						keys[i, 'y'] = val * self.Keyframes.pixelscale
						keys[i, 'expression'] = 'linear()'
		finally:
			self._LogEnd()

SANITY = 20000

class _Parser:
	def __init__(self, host, indat, verbose=False):
		self.host = host
		self.indat = indat
		self.verbose = verbose
		self.row = 0
		self.output = KeyframeSet()

	@property
	def _State(self):
		if not self.verbose:
			return ''
		cells = self.indat.row(self.row)
		return '       | cells: {0!r}'.format([repr(c.val) for c in cells] if cells else 'None')

	def _FormatEvent(self, event):
		return '[{}] {}{}'.format(self.row, event, self._State)

	def _LogBegin(self, event):
		self.host.LogBegin(self._FormatEvent(event))

	def _Log(self, event):
		if self.verbose:
			self.host.LogEvent(self._FormatEvent(event))

	def _LogEnd(self, event=None):
		if event:
			self.host.LogEnd(self._FormatEvent(event))
		else:
			self.host.LogEnd()

	def _GoToNextRow(self):
		self.row += 1

	def _LogCurrentRow(self):
		cells = self.indat.row(self.row)
		self._Log('current row : {0!r}'.format([repr(c.val) for c in cells] if cells else 'None'))

	def _ParseHeaderAttrs(self):
		try:
			self._LogBegin('_ParseHeaderAttrs()')
			compattrs = {}
			while self.row < self.indat.numRows:
				if self.indat[self.row, 1] == '':
					break
				self.row += 1
				compattrs[self.indat[self.row, 1].val] = self.indat[self.row, 2].val
			return compattrs
		finally:
			self._LogEnd()

	def Parse(self):
		self._LogBegin('Parse()')
		try:
			self._GoToNextRow()
			self._GoToNextRow()
			if self.row >= self.indat.numRows:
				return
			self.output = KeyframeSet(self._ParseHeaderAttrs())
			if not self._GoToNextBlankRow(1):
				return
			self._GoToNextRow()
			sanity = SANITY
			while self.row < self.indat.numRows:
				self._LogBegin('Parse() - scanning row {}...'.format(self.row))
				self._LogCurrentRow()
				try:
					if self.indat[self.row, 0] == 'End of Keyframe Data':
						return
					if sanity == 0:
						raise Exception('INSANITY!!!')
					sanity -= 1
					block = self._ParseNextBlock()
					self.output.blocks.append(block)
					if self.indat[self.row, 0] == '':
						self._GoToNextRow()
					if self.indat[self.row, 0] == '':
						self._GoToNextRow()
				finally:
					self._LogEnd()
		finally:
			self._LogEnd()

	def _GoToNextBlankRow(self, col):
		self._LogBegin('_GoToNextBlankRow()')
		try:
			self._GoToNextRow()
			sanity = SANITY
			while self.row < self.indat.numRows:
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
			# group = indat[self.row, 0].val
			# components = indat[self.row, 1].val
			param = indat[self.row, 2].val
			# blockname = '{}/{}/{}'.format(group, components, param)
			# blockname = '{}/{}'.format(components, param)
			blockname = _StripNumSuffix(param)
			block = Block(
				name=blockname,
				attrnames=[
					_CleanAttrib(indat[self.row, i].val)
					for i in range(2, indat.numCols)
					if indat[self.row, i].val != ''
				])
			self._Log('_ParseNextBlock() - block name: {}'.format(block.name))
			self._GoToNextRow()
			self._Log('_ParseNextBlock() - attrs: {}'.format(block.attrs.keys()))
			sanity = SANITY
			numframes = 0
			while self.row < self.indat.numRows:
				self._GoToNextRow()
				if sanity == 0:
					raise Exception('INSANITY!!!')
				sanity -= 1
				if indat[self.row, 1] == '':
					self._Log('_ParseNextBlock() - found blank row in block. stopping')
					break
				f = int(indat[self.row, 1])
				if f > self.output.maxframe:
					self.output.maxframe = f
				for i, attr in enumerate(block.attrs):
					block.attrs[attr].append([f, float(indat[self.row, i + 2])])
				numframes += 1
			self._Log('_ParseNextBlock() - found {} frames'.format(numframes))
			return block
		finally:
			self._LogEnd()

class Block:
	def __init__(self, name, attrnames):
		self.name = name
		self.attrs = {
			attr: []
			for attr in attrnames
		}

class KeyframeSet:
	def __init__(self, attrs=None):
		if attrs is None:
			attrs = {}
		self.attrs = attrs
		self.width = util.ParseFloat(attrs.get('Source Width'), 1)
		self.height = util.ParseFloat(attrs.get('Source Height'), 1)
		self.pixelscale = 1.0 / min(self.width, self.height)
		self.fps = util.ParseFloat(attrs.get('Units Per Second'), 30)
		self.maxframe = 0
		self.blocks = []

	def __repr__(self):
		return 'KeyframeSet(w:{}, h:{}, fps:{}, maxframe:{}, blocks:{})'.format(
			self.width, self.height, self.fps, self.maxframe, len(self.blocks))

def _Clean(n):
	return tdu.legalName(n)

_numSuffixRx = re.compile(r'\s*#\d+')
def _StripNumSuffix(s):
	return _numSuffixRx.sub('', s)

_pixelsSuffix = re.compile(r' pixels$')
def _CleanAttrib(s):
	return _pixelsSuffix.sub('', s)

def _IsPixels(s):
	return _pixelsSuffix.match(s)
