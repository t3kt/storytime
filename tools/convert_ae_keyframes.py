import sys
import os
import re
import json
import argparse

def _initPath():
	basedir = os.path.dirname(__file__)
	for parts in [
		['..', 'common', 'lib'],
		['..', 'lib'],
	]:
		sys.path.append(os.path.join(basedir, *parts))
	pass
_initPath()
del _initPath

import util
_ParseFloat = util.ParseFloat
from ae_keyframes import KeyframeSet, Block

def _SplitLines(infile):
	lines = []
	for line in infile.readlines():
		line = line.rstrip('\r\n')
		lines.append(line.split('\t') if line else [])
	return lines

class Parser:
	def __init__(self, inputrows, verbose=False):
		self.logger = util.IndentedLogger(outfile=sys.stderr)
		self.inputrows = inputrows
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
		if self.verbose:
			self.logger.LogBegin('', '', self._FormatEvent(event))

	def _Log(self, event):
		if self.verbose:
			self.logger.LogEvent('', '', self._FormatEvent(event))

	def _LogEnd(self, event=None):
		if self.verbose:
			self.logger.LogEnd('', '', self._FormatEvent(event))

	def _GoToNextRow(self):
		self.row += 1
		if self.row < len(self.inputrows):
			self.rowcells = self.inputrows[self.row]
			return True
		else:
			self.rowcells = []
			return False

	def _LogCurrentRow(self, message=None):
		self._Log('{0} current row : {1!r}'.format(
			message or '',
			self.inputrows[self.row]))

	def _Cell(self, col):
		if not self.rowcells:
			return None
		if col >= len(self.rowcells):
			return None
		return self.rowcells[col]

	def _ParseCompAttrs(self):
		compattrs = {}
		self._LogBegin('_ParseCompAttrs()')
		try:
			while self.row < len(self.inputrows):
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
			while self.row < len(self.inputrows):
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
					while not self._Cell(0):
						if self._GoToNextRow():
							return
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
					attr
					for attr in self.rowcells[2:]
					if attr
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

def _WriteKeyframeSet(frameset, out):
	out.write('OMG KEYFRAME SET: ' + repr(frameset))

def main():
	parser = argparse.ArgumentParser(description='Convert After Effects keyframe data')
	parser.add_argument(
		'inpath', type=str,
		help='Keyframe data input file')
	parser.add_argument(
		'-o', '--output', type=str,
		help='Output file')
	parser.add_argument(
		'-v', '--verbose', type=bool, default=False,
		help='Verbose logging')
	parser.add_argument(
		'-p', '--pretty', type=bool, default=False,
		help='Pretty-print output JSON')
	args = parser.parse_args()
	if args.verbose:
		print('Reading from ' + args.inpath, file=sys.stderr)
	with open(args.inpath, 'r') as infile:
		inputrows = _SplitLines(infile)
	parser = Parser(inputrows, verbose=args.verbose)
	parser.Parse()
	frameset = parser.output
	print('Keyframe data: ', frameset, file=sys.stderr)
	if args.output:
		with open(args.output, 'w') as outfile:
			json.dump(frameset.toJson(), outfile)
		print('Saved to ' + args.output, file=sys.stderr)
	else:
		json.dump(frameset.toJson(), sys.stdout)

if __name__ == '__main__':
	main()
