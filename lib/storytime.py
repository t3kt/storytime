try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

from storytimedb import *

if False:
	from _stubs import *

class StoryDbManager(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.Db = StoryDb()
		self.LoadDatabase()

	def LoadDatabase(self):
		self._LogBegin('LoadDatabase()')
		try:
			dbpath = self.comp.par.Dbfile.eval()
			if not dbpath:
				return
			self.Db.load(dbpath)
			# for o in self.comp.ops('./build_*'):
			# 	o.cook(force=True)
		finally:
			self._LogEnd()

	@property
	def Tellers(self):
		return self.Db.tellers.values()

	def BuildTellerTable(self, dat):
		dat.clear()
		dat.appendRow(['name', 'label', 'storycount'])
		for teller in self.Tellers:
			dat.appendRow([
				teller.name,
				teller.label,
				len(teller.stories),
			])

	def BuildStoryTable(self, dat):
		dat.clear()
		dat.appendRow(['id', 'teller', 'story', 'label', 'duration', 'segmentcount', 'vidfile'])
		for teller in self.Tellers:
			for story in teller.stories.values():
				row = dat.numRows
				dat.appendRow([])
				dat[row, 'id'] = '{0}/{1}'.format(teller.name, story.name)
				dat[row, 'teller'] = teller.name
				dat[row, 'story'] = story.name
				dat[row, 'duration'] = story.duration
				dat[row, 'segmentcount'] = len(story.segments)
				dat[row, 'vidfile'] = story.videofile

	def BuildSegmentTable(self, dat):
		dat.clear()
		dat.appendRow([
			'id', 'teller', 'story', 'index',
			'start', 'end', 'duration',
			'start_fraction', 'end_fraction',
			'text', 'vidfile'
		])
		for teller in self.Tellers:
			for story in teller.stories.values():
				for index, segment in enumerate(story.segments):
					row = dat.numRows
					dat.appendRow([])
					dat[row, 'id'] = '{0}/{1}/{2}'.format(teller.name, story.name, index)
					dat[row, 'teller'] = teller.name
					dat[row, 'story'] = story.name
					dat[row, 'index'] = index
					dat[row, 'start'] = segment.start
					dat[row, 'end'] = segment.end
					dat[row, 'start_fraction'] = segment.start / story.duration
					dat[row, 'end_fraction'] = segment.end / story.duration
					dat[row, 'duration'] = segment.duration
					dat[row, 'text'] = segment.text
					dat[row, 'vidfile'] = story.videofile
