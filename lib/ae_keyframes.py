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
		self.Keyframes = KeyframeSet()

	@property
	def _Verbose(self):
		return self.comp.par.Verbose.eval()

	def LoadKeyframes(self):
		self.LogBegin('LoadKeyframes()')
		try:
			datatable = self.comp.op('./key_data_table')
			datatable.par.loadonstart.pulse()

			compattrs = self._GetCompAttrs()

			parser = Parser(
				self,
				datatable,
				compattrs=compattrs,
				verbose=self._Verbose)
			parser.Parse()
			self.Keyframes = parser.output
			self.LogEvent('LoadKeyframes() keyframes: {0!r}'.format(self.Keyframes))
			self._WriteKeyframes()
		finally:
			self.LogEnd()

	def _WriteKeyframes(self):
		self.LogBegin('_WriteKeyframes()')
		try:
			channels = self.animation.op('./channels')
			keys = self.animation.op('./keys')
			channels.clear(keepFirstRow=True)
			keys.clear(keepFirstRow=True)
			self.animation.time.rate = self.Keyframes.fps
			self.animation.time.end = self.Keyframes.maxframe or 1
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
					valscale = self.Keyframes.pixelscale if _IsPixels(blockname) else 1
					for f, val in frames:
						i = keys.numRows
						keys.appendRow([])
						keys[i, 'id'] = chanid
						keys[i, 'x'] = f + 1
						keys[i, 'y'] = val * valscale
						keys[i, 'expression'] = 'linear()'
		finally:
			self.LogEnd()

	def _GetCompAttrs(self):
		vals = self.comp.op('./comp_vals')
		compattrs = {
			c.name: float(c)
			for c in vals.chans('*')
		}
		if self._Verbose:
			self.LogEvent('_GetCompAttrs() - {}'.format(compattrs))
		return compattrs

class Parser:
	def __init__(self, host, indat, compattrs, verbose=False):
		self.host = host
		self.indat = indat
		self.verbose = verbose
		self.row = 0
		self.output = KeyframeSet(compattrs)
		self.sanity = 100000

	def _SanityTick(self):
		self.sanity -= 1
		if self.sanity <= 0:
			raise Exception('INSANITY ACHIEVED!!')

	def _FormatEvent(self, event):
		return '[{}] {} (SANITY: {})'.format(self.row, event, self.sanity)

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

	def _LogCurrentRow(self, message=None):
		cells = self.indat.row(self.row)
		self._Log('{0} current row : {1!r}'.format(
			message or '',
			[repr(c.val) for c in cells] if cells else 'None'))

	def Parse(self):
		self._LogBegin('Parse()')
		try:
			self.row = 3
			if self.row >= self.indat.numRows:
				return
			if not self._GoToNextBlankRow(0):
				return
			self._GoToNextRow()
			self._LogCurrentRow('Parse() - starting to parse blocks')
			while self.row < self.indat.numRows:
				self._LogBegin('Parse() - scanning row {}...'.format(self.row))
				self._LogCurrentRow()
				try:
					if self.indat[self.row, 0] == 'End of Keyframe Data':
						return
					self._SanityTick()
					block = self._ParseNextBlock()
					self._GoToNextRow()
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
			while self.row < self.indat.numRows:
				self._SanityTick()
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
			self._Log('_ParseNextBlock() - attrs: {}'.format(list(block.attrs.keys())))
			numframes = 0
			while self.row < self.indat.numRows:
				self._SanityTick()
				self._GoToNextRow()
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
		self.width = util.ParseFloat(attrs.get('Source_Width'), 1)
		self.height = util.ParseFloat(attrs.get('Source_Height'), 1)
		self.pixelscale = 1.0 / min(self.width, self.height)
		self.fps = util.ParseFloat(attrs.get('Units_Per_Second'), 30)
		self.fps = float(attrs['Unit_Per_Second']) if attrs else None
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
