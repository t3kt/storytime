import sys
import json
import argparse
import re

import common.lib.util as util
from storytime.ae_keyframes import KeyframeSet, Block, StripNumSuffix

_ParseFloat = util.ParseFloat

def eprint(*args):
	print(*args, file=sys.stderr)

def _SplitLines(infile):
	lines = []
	for line in infile.readlines():
		line = line.rstrip('\r\n')
		lines.append(line.split('\t') if line else [])
	return lines

class AEKeyframeParser:
	def __init__(self, inputrows, verbose=False):
		self.logger = util.IndentedLogger(outfile=sys.stderr)
		self.inputrows = inputrows
		self.verbose = verbose
		self.row = 0
		self.frameset = KeyframeSet()

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
			self.frameset = KeyframeSet(self._ParseCompAttrs())
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
					self.frameset.blocks.append(block)
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
			blockname = StripNumSuffix(param)
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
				if f > self.frameset.maxframe:
					self.frameset.maxframe = f
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
		self.infopath = args.info
		self.channelspath = args.channels
		self.keyspath = args.keys
		if args.format in ['json', 'text']:
			self.format = args.format
		elif self.outpath:
			self.format = 'json' if self.outpath.endswith('.json') else 'text'
		else:
			self.format = 'json'
		self.frameset = None

	def Run(self):
		if self.verbose:
			eprint('Reading from ' + self.inpath)
		with open(self.inpath, 'r') as infile:
			inputrows = _SplitLines(infile)
		parser = AEKeyframeParser(inputrows, verbose=self.verbose)
		parser.Parse()
		self.frameset = parser.frameset
		eprint('Keyframe data: ', self.frameset)
		if self.outpath:
			with open(self.outpath, 'w') as outfile:
				if self.format == 'json':
					self._WriteJson(outfile)
				else:
					self._WriteText(outfile)
			eprint('Saved to ', self.outpath)
		if self.infopath:
			with open(self.infopath, 'w') as outfile:
				json.dump(self.frameset.infoJson(), outfile, indent='  ')
			eprint('Wrote info to ', self.infopath)
		if self.channelspath:
			with open(self.channelspath, 'w') as outfile:
				self._WriteChannels(outfile)
			eprint('Wrote channels to ', self.channelspath)
		if self.keyspath:
			with open(self.keyspath, 'w') as outfile:
				self._WriteKeys(outfile)
			eprint('Wrote keys to ', self.keyspath)
		if not any([self.outpath, self.infopath, self.channelspath, not self.keyspath]):
			if self.format == 'json':
				self._WriteJson(sys.stdout)
			else:
				self._WriteText(sys.stdout)

	def _WriteText(self, out):
		writer = DATWriter(out)
		writer.AppendRow(['!i', json.dumps(self.frameset.infoJson())])
		for block in self.frameset.blocks:
			writer.AppendRow(['!b', block.name])
			for attr, frames in block.attrs.items():
				writer.AppendRow(['!a', attr])
				for f, val in frames:
					writer.AppendRow(['!f', f, val])

	def _WriteChannels(self, out):
		writer = DATWriter(out, cols=[
			'name', 'id',  'left', 'right', 'default', 'keys',
			'liner', 'lineg', 'lineb', 'picked', 'display', 'template',
		])
		writer.WriteHeader()
		chanid = 0
		for block in self.frameset.blocks:
			for attr, _ in block.attrs.items():
				chanid += 1
				writer.AppendRow({
					'name': '{}:{}'.format(_Clean(block.name), _Clean(attr)),
					'id': chanid,
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

	def _WriteKeys(self, out):
		writer = DATWriter(out, cols=[
			'id', 'x', 'y',
			'inslope', 'inaccel',
			'expression',
			'outslope', 'outaccel',
		])
		writer.WriteHeader()
		chanid = 0
		for block in self.frameset.blocks:
			for attr, frames in block.attrs.items():
				chanid += 1
				# valscale = self.frameset.pixelscale if IsPixels(attr) else 1
				for f, val in frames:
					writer.AppendRow({
						'id': chanid,
						'x': f + 1,
						'y': val,  # * valscale,
						'expression': 'linear()',
					})

	def _WriteJson(self, out):
		json.dump(
			self.frameset.toJson(), out,
			indent='  ' if self.pretty else None)

def _Clean(s):
	return re.sub('[^a-zA-Z0-9_]', '_', s).strip('_') if s else ''

class DATWriter:
	def __init__(self, out, cols=None):
		self.out = out
		self.cols = cols

	def WriteHeader(self):
		if self.cols:
			self._WriteLine(self.cols)

	def _WriteLine(self, cells):
		self.out.write('\t'.join([str(cell) for cell in cells]))
		self.out.write('\n')

	def AppendRow(self, cells):
		if isinstance(cells, dict):
			self._WriteLine([
				str(cells.get(self.cols[i], ''))
				for i in range(len(self.cols))
			])
		else:
			self._WriteLine(cells)

def main():
	parser = argparse.ArgumentParser(description='Convert After Effects keyframe data')
	parser.add_argument(
		'inpath', type=str,
		help='Keyframe data input file')
	parser.add_argument(
		'-o', '--output', type=str,
		help='Output file')
	parser.add_argument(
		'-i', '--info', type=str,
		help='Info output file')
	parser.add_argument(
		'-c', '--channels', type=str,
		help='Channels output file')
	parser.add_argument(
		'-k', '--keys', type=str,
		help='Keys output file')
	parser.add_argument(
		'-f', '--format', type=str, default='auto',
		choices=['json', 'text', 'auto'],
		help='Output format')
	parser.add_argument(
		'-v', '--verbose', action='store_true',
		help='Verbose logging')
	parser.add_argument(
		'-p', '--pretty', type=bool, default=False,
		help='Pretty-print output JSON')
	args = parser.parse_args()
	tool = ConverterTool(args)
	tool.Run()

if __name__ == '__main__':
	main()
