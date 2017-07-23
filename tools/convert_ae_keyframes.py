import sys
import os
import re

def _initPath():
	basedir = os.path.dirname(__file__)
	for parts in [
		['..', 'common', 'lib'],
	]:
		sys.path.append(os.path.join(basedir, *parts))
	pass
_initPath()
del _initPath

import util
_ParseFloat = util.ParseFloat

class Host:
	def __init__(self):
		self.logger = util.IndentedLogger()

	def LogEvent(self, event):
		self.logger.LogEvent('', '', event)

	def LogBegin(self, event):
		self.logger.LogBegin('', '', event)

	def LogEnd(self, event=None):
		self.logger.LogEnd('', '', event)

def _SplitLines(infile):
	lines = []
	# maxcount = 0
	# for line in infile.readlines():
	# 	parts = line.split('\t')
	# 	if len(parts) > maxcount:
	# 		maxcount = len(parts)
	# 		lines.append(parts)
	# for i in range(len(lines)):
	# 	parts = lines[i]
	# 	while len(parts) < maxcount:
	# 		parts.append('')
	for line in infile.readlines():
		line = line.rstrip('\r\n')
		lines.append(line.split('\t') if line else [])
	return lines

class Parser:
	def __init__(self, inlines, verbose=False):
		self.logger = util.IndentedLogger()
		self.inlines = inlines
		self.verbose = verbose
		self.row = 0
		self.output = KeyframeSet()
		# self.sanity = 100000

	def _SanityTick(self):
		# self.sanity -= 1
		# if self.sanity <= 0:
		# 	raise Exception('INSANITY ACHIEVED!!')
		pass

	def _FormatEvent(self, event):
		if not event:
			return ''
		# return '[{}] {} (SANITY: {})'.format(self.row, event, self.sanity)
		return '[{}] {}'.format(self.row, event)

	def _LogBegin(self, event):
		self.logger.LogBegin('', '', self._FormatEvent(event))

	def _Log(self, event):
		if self.verbose:
			self.logger.LogEvent('', '', self._FormatEvent(event))

	def _LogEnd(self, event=None):
		self.logger.LogEnd('', '', self._FormatEvent(event))

	def _GoToNextRow(self):
		self.row += 1
		if self.row < len(self.inlines):
			self.rowcells = self.inlines[self.row]
			return True
		else:
			self.rowcells = []
			return False

	def _LogCurrentRow(self, message=None):
		self._Log('{0} current row : {1!r}'.format(
			message or '',
			self.inlines[self.row]))

	def _Cell(self, col):
		if self.row >= len(self.inlines):
			return None
		parts = self.inlines[self.row]
		if col >= len(parts):
			return None
		return parts[col]

	def _ParseCompAttrs(self):
		compattrs = {}
		self._LogBegin('_ParseCompAttrs()')
		try:
			while self.row < len(self.inlines):
				if not self._Cell(1):
					break
				compattrs[self._Cell(1)] = _ParseFloat(self._Cell(2))
				self._GoToNextRow()
			return compattrs
		finally:
			self._LogEnd('_ParseCompAttrs() - {}'.format(compattrs))

	def Parse(self):
		self._LogBegin('Parse()')
		try:
			if not self._GoToNextRow():
				return
			if not self._GoToNextRow():
				return
			self.output = KeyframeSet(self._ParseCompAttrs())
			self._GoToNextRow()
			self._LogCurrentRow('Parse() - starting to parse blocks')
			while self.row < len(self.inlines):
				if not self._Cell(0):
					return
				self._LogBegin('Parse() - scanning row {}...'.format(self.row))
				self._LogCurrentRow()
				try:
					if self._Cell(0) == 'End of Keyframe Data':
						return
					self._SanityTick()
					block = self._ParseNextBlock()
					if not block:
						return
					self.output.blocks.append(block)
					if not self._GoToNextRow():
						return
					if self._Cell(0) == '':
						self._GoToNextRow()
					if self._Cell(0) == '':
						self._GoToNextRow()
				finally:
					self._LogEnd()
		finally:
			self._LogEnd()

	def ZZZZ_GoToNextBlankRow(self, col):
		self._LogBegin('_GoToNextBlankRow()')
		try:
			while self._GoToNextRow():
				self._SanityTick()
				if self._Cell(col) == '':
					return True
			return False
		finally:
			self._LogEnd()

	def _ParseNextBlock(self):
		self._LogBegin('_ParseNextBlock()')
		try:
			# group = self._Cell(0)
			# components = self._Cell(1)
			param = self._Cell(2)
			# blockname = '{}/{}/{}'.format(group, components, param)
			# blockname = '{}/{}'.format(components, param)
			blockname = _StripNumSuffix(param)
			if not self._GoToNextRow():
				return
			block = Block(
				name=blockname,
				attrnames=[
					_CleanAttrib(self._Cell(i))
					for i in range(2, len(self.rowcells))
					if self._Cell(i) != ''
				])
			self._Log('_ParseNextBlock() - block name: {}'.format(block.name))
			self._Log('_ParseNextBlock() - attrs: {}'.format(list(block.attrs.keys())))
			numframes = 0
			while self._GoToNextRow():
				self._SanityTick()
				if not self._Cell(1):
					self._Log('_ParseNextBlock() - found blank row in block. stopping')
					break
				f = int(self._Cell(1))
				if f > self.output.maxframe:
					self.output.maxframe = f
				for i, attr in enumerate(block.attrs):
					block.attrs[attr].append([f, float(self._Cell(i + 2))])
				numframes += 1
			self._Log('_ParseNextBlock() - found {} frames'.format(numframes))
			return block
		finally:
			self._LogEnd()

_numSuffixRx = re.compile(r'\s*#\d+')
def _StripNumSuffix(s):
	return _numSuffixRx.sub('', s)

_pixelsSuffix = re.compile(r' pixels$')
def _CleanAttrib(s):
	return _pixelsSuffix.sub('', s)

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
		self.width = _ParseFloat(attrs.get('Source Width'), 1)
		self.height = _ParseFloat(attrs.get('Source Height'), 1)
		self.pixelscale = 1.0 / min(self.width, self.height)
		self.fps = _ParseFloat(attrs.get('Units Per Second'), 30)
		self.maxframe = 0
		self.blocks = []

	def __repr__(self):
		return 'KeyframeSet(w:{}, h:{}, fps:{}, maxframe:{}, blocks:{})'.format(
			self.width, self.height, self.fps, self.maxframe, len(self.blocks))

def _WriteKeyframeSet(frameset, out):
	out.write('OMG KEYFRAME SET: ' + repr(frameset))

def main(args):
	inpath = None
	outpath = None
	verbose = False
	if len(args) == 4:
		if args[1] != '-v':
			usage(args)
		verbose = True
		inpath = args[2]
		outpath = args[3]
	elif len(args) == 3:
		verbose = False
		inpath = args[1]
		outpath = args[2]
	else:
		usage(args)
	print('INPUT:  ' + inpath)
	print('OUTPUT: ' + outpath)
	with open(inpath, 'r') as infile:
		inlines = _SplitLines(infile)
	parser = Parser(inlines, verbose=verbose)
	parser.Parse()
	frameset = parser.output
	print('LOL KEYFRAME SET', frameset)
	pass

def usage(args):
	print('USAGE: python {} <input-file> <output-file>'.format(args[0]))
	exit(1)

if __name__ == '__main__':
	main(sys.argv)
