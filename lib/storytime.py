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

import pysrt
# from moviepy.editor import *
import datetime

def _SrtTimeToSeconds(t):
	return (t.to_time() - datetime.time()).total_seconds()

class SubtitleLoader(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)

	def _LoadSubFile(self):
		path = self.comp.par.Subfile.eval()
		if path:
			return pysrt.open(path)
		textdat = self.comp.par.Textdat.eval()
		if not textdat or not textdat.text:
			return None
		return pysrt.from_string(textdat.text)

	def FillCaptionTable(self, dat):
		dat.clear()
		dat.appendRow(['start', 'end', 'duration', 'start_time', 'end_time', 'duration_time', 'clean_text', 'raw_text'])
		subfile = self._LoadSubFile()
		if not subfile:
			return
		for item in subfile:
			dat.appendRow([
				item.start.ordinal / 1000,
				item.end.ordinal / 1000,
				item.duration.ordinal / 1000,
				item.start,
				item.end,
				item.duration,
				item.text_without_tags,
				item.text,
			])

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
		dat.appendRow(['id', 'teller', 'story', 'label', 'duration', 'segmentcount'])
		for teller in self.Tellers:
			for story in teller.stories.values():
				dat.appendRow([
					'{0}/{0}'.format(teller.name, story.name),
					teller.name,
					story.name,
					story.label,
					story.duration,
					len(story.segments),
				])

	def BuildSegmentTable(self, dat):
		dat.clear()
		dat.appendRow(['id', 'teller', 'story', 'index', 'start', 'end', 'duration', 'text'])
		for teller in self.Tellers:
			for story in teller.stories.values():
				for index, segment in enumerate(story.segments):
					row = dat.numRows
					dat.appendRow([])
					dat[row, 'id'] = '{0}/{0}/{0}'.format(teller.name, story.name, index)
					dat[row, 'teller'] = teller.name
					dat[row, 'story'] = story.name
					dat[row, 'index'] = index
					dat[row, 'start'] = segment.start
					dat[row, 'end'] = segment.end
					dat[row, 'duration'] = segment.duration
					dat[row, 'text'] = segment.text
