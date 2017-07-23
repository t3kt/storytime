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

def eprint(*args):
	print(*args, file=sys.stderr)

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

	def _FormatEvent(self, event):
		return '[{}] {}'.format(self.row, event) if event else ''

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

class ConverterTool:
	def __init__(self, args):
		self.inpath = args.inpath
		self.verbose = args.verbose
		self.outpath = args.output
		self.pretty = args.pretty
		if args.format in ['json', 'text']:
			self.format = args.format
		elif self.outpath:
			self.format = 'json' if self.outpath.endswith('.json') else 'text'
		else:
			self.format = 'json'

	def Run(self):
		if self.verbose:
			eprint('Reading from ' + self.inpath)
		with open(self.inpath, 'r') as infile:
			inputrows = _SplitLines(infile)
		parser = Parser(inputrows, verbose=self.verbose)
		parser.Parse()
		frameset = parser.output
		eprint('Keyframe data: ', frameset)
		if self.outpath:
			with open(self.outpath, 'w') as outfile:
				if self.format == 'json':
					self._WriteJson(frameset, outfile)
				else:
					self._WriteText(frameset, outfile)
			eprint('Saved to ', self.outpath)
		else:
			if self.format == 'json':
				self._WriteJson(frameset, sys.stdout)
			else:
				self._WriteText(frameset, sys.stdout)

	@staticmethod
	def _WriteText(frameset, out):
		def writeline(parts):
			out.write('\t'.join([str(part) for part in parts]))
			out.write('\n')
		writeline(['!i', json.dumps(frameset.infoJson())])
		for block in frameset.blocks:
			writeline(['!b', block.name])
			for attr, frames in block.attrs.items():
				writeline(['!a', attr])
				for f, val in frames:
					writeline(['!f', f, val])

	def _WriteJson(self, frameset, out):
		json.dump(
			frameset.toJson(), out,
			indent='  ' if self.pretty else None)

_numSuffixRx = re.compile(r'\s*#\d+')
def _StripNumSuffix(s):
	return _numSuffixRx.sub('', s)


def main():
	parser = argparse.ArgumentParser(description='Convert After Effects keyframe data')
	parser.add_argument(
		'inpath', type=str,
		help='Keyframe data input file')
	parser.add_argument(
		'-o', '--output', type=str,
		help='Output file')
	parser.add_argument(
		'-f', '--format', type=str, default='auto',
		choices=['json', 'text', 'auto'],
		help='Output format')
	parser.add_argument(
		'-v', '--verbose', type=bool, default=False,
		help='Verbose logging')
	parser.add_argument(
		'-p', '--pretty', type=bool, default=False,
		help='Pretty-print output JSON')
	args = parser.parse_args()
	tool = ConverterTool(args)
	tool.Run()

if __name__ == '__main__':
	main()
