import re
import json

try:
	import common_base as base
except ImportError:
	try:
		import common.lib.base as base
	except ImportError:
		import base

try:
	import common_util as util
except ImportError:
	try:
		import common.lib.util as util
	except ImportError:
		import util

if False:
	from _stubs import *

class FastKeyframeLoader(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.animation = comp.op('./animation')
		self.Keyframes = KeyframeSet()

	def LoadKeyframes(self):
		self.LogBegin('LoadKeyframes()')
		try:
			infopath = self.comp.par.Infofile.eval()
			if infopath:
				with open(infopath, 'r') as infile:
					obj = json.load(infile)
				self.Keyframes = KeyframeSet.fromJson(obj)
				self.animation.time.rate = self.Keyframes.fps
				self.animation.time.end = self.Keyframes.maxframe or 1
			channels = self.animation.op('./channels')
			if channels.par.file.eval():
				self.LogEvent('LoadKeyframes() - loading channels from {}'.format(channels.par.file.eval()))
				channels.par.loadonstart.pulse()
				channels.cook(force=True)
			else:
				self.LogEvent('LoadKeyframes() - no channels file to load!')
				channels.clear(keepFirstRow=True)
			keys = self.animation.op('./keys')
			if keys.par.file.eval():
				self.LogEvent('LoadKeyframes() - loading keys from {}'.format(keys.par.file.eval()))
				keys.par.loadonstart.pulse()
				keys.cook(force=True)
			else:
				self.LogEvent('LoadKeyframes() - no keys file to load!')
				keys.clear(keepFirstRow=True)
		finally:
			self.LogEnd()

class Block:
	def __init__(
			self,
			name,
			attrnames=None,
			attrs=None):
		self.name = name
		self.attrs = attrs or {
			attr: []
			for attr in attrnames or []
		}

	def applyFrameOffset(self, amount):
		for frames in self.attrs.values():
			for frame in frames:
				frame[0] += amount

	def mergeFrom(self, otherblock: 'Block', validateonly=False):
		mismatches = set(self.attrs.keys()).symmetric_difference(otherblock.attrs.keys())
		if mismatches:
			raise Exception('Invalid block merge! Blocks have different keys: {}'.format(mismatches))
		if not validateonly:
			for attr in self.attrs.keys():
				self.attrs[attr] += otherblock.attrs[attr]

	def __repr__(self):
		return 'Block({}, attrs:{})'.format(
			self.name,
			{attr: len(vals) for attr, vals in self.attrs.items()})

	@classmethod
	def fromJson(cls, obj):
		return cls(
			name=obj['name'],
			attrs=obj['attrs'],
		)

	def toJson(self):
		return {
			'name': self.name,
			'attrs': self.attrs,
		}

class KeyframeSet:
	def __init__(
			self,
			attrs=None,
			width=None, height=None, fps=None,
			maxframe=None,
			blocks=None):
		if attrs is None:
			attrs = {}
		self.attrs = attrs
		self.width = int(width or util.ParseFloat(attrs.get('Source Width'), 1))
		self.height = int(height or util.ParseFloat(attrs.get('Source Height'), 1))
		self.pixelscale = 1.0 / min(self.width, self.height)
		self.fps = fps or util.ParseFloat(attrs.get('Units Per Second'), 30)
		self.maxframe = maxframe or 0
		self.blocks = blocks or []

	def applyFrameOffset(self, amount):
		for block in self.blocks:
			block.applyFrameOffset(amount)

	def mergeFrom(self, otherFrameset: 'KeyframeSet', validateonly=False):
		ownblocks = self.getBlocksByName()
		otherblocks = otherFrameset.getBlocksByName()
		mismatches = set(ownblocks.keys()).symmetric_difference(otherblocks.keys())
		if mismatches:
			raise Exception('Invalid frameset merge! Framesets have different blocks: {}'.format(mismatches))
		for blockname, ownblock in ownblocks.items():
			otherblock = otherblocks[blockname]
			ownblock.mergeFrom(otherblock, validateonly=validateonly)

	def getBlocksByName(self):
		return {block.name: block for block in self.blocks}

	@classmethod
	def fromJson(cls, obj):
		return cls(
			attrs=obj.get('attrs'),
			width=obj.get('width'),
			height=obj.get('height'),
			fps=obj.get('fps'),
			maxframe=obj.get('maxframe'),
			blocks=[
				Block.fromJson(bobj)
				for bobj in obj.get('blocks', [])
			]
		)

	def __repr__(self):
		return 'KeyframeSet(w:{}, h:{}, fps:{}, maxframe:{}, blocks:{})'.format(
			self.width, self.height, self.fps, self.maxframe, len(self.blocks))

	def infoJson(self):
		return {
			'attrs': self.attrs,
			'width': self.width,
			'height': self.height,
			'fps': self.fps,
			'maxframe': self.maxframe,
		}

	def toJson(self):
		return util.MergeDicts(
			self.infoJson(),
			{
				'blocks': [b.toJson() for b in self.blocks],
			}
		)

def _Clean(n):
	return tdu.legalName(n)

_numSuffixRx = re.compile(r'\s*#\d+')
def StripNumSuffix(s):
	return _numSuffixRx.sub('', s)
