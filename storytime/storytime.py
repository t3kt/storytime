try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

from storytimedb import *
import random
from typing import Dict, Iterable, List, Optional

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
	def Tellers(self) -> Iterable[StoryTeller]:
		return self.Db.tellers.values()

	def BuildTellerTable(self, dat):
		dat.clear()
		dat.appendRow(['name', 'label', 'storycount'])
		for teller in self.Tellers:
			if teller.disabled:
				continue
			dat.appendRow([
				teller.name,
				teller.label,
				len(teller.stories),
			])

	def BuildStoryTable(self, dat):
		dat.clear()
		dat.appendRow(['id', 'teller', 'story', 'label', 'duration', 'fps', 'segmentcount', 'vidfile'])
		for teller in self.Tellers:
			for story in teller.stories.values():
				row = dat.numRows
				dat.appendRow([])
				dat[row, 'id'] = '{0}/{1}'.format(teller.name, story.name)
				dat[row, 'teller'] = teller.name
				dat[row, 'story'] = story.name
				dat[row, 'label'] = story.label
				dat[row, 'duration'] = story.duration
				dat[row, 'fps'] = story.fps
				dat[row, 'segmentcount'] = len(story.segments)
				dat[row, 'vidfile'] = story.videofile

	def BuildSegmentTable(self, dat):
		dat.clear()
		dat.appendRow([
			'id', 'teller', 'story', 'index',
			'start', 'end', 'duration',
			'start_fraction', 'end_fraction',
			'text',
		])
		minduration = self.comp.par.Minsegmentlength.eval()
		for teller in self.Tellers:
			if teller.disabled:
				continue
			for story in teller.stories.values():
				if story.disabled:
					continue
				for index, segment in enumerate(story.enabledSegments):
					if segment.duration < minduration:
						continue
					if segment.disabled:
						continue
					row = dat.numRows
					dat.appendRow([])
					dat[row, 'id'] = '{0}/{1}/{2}'.format(teller.name, story.name, index)
					dat[row, 'teller'] = teller.name
					dat[row, 'story'] = story.name
					dat[row, 'index'] = index
					dat[row, 'start'] = segment.start
					dat[row, 'end'] = segment.end
					dat[row, 'start_fraction'] = segment.startFraction
					dat[row, 'end_fraction'] = segment.endFraction
					dat[row, 'duration'] = segment.duration
					dat[row, 'text'] = segment.text

def _GetDbManager() -> StoryDbManager:
	return op.Storydb

class StoryPlayer(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.Story = None  # type: Story
		self.Teller = None  # type: StoryTeller
		self.ReattachStory()
		self.timer = self.comp.op('./timer')
		self.segvals = self.comp.op('./segment_vals')

	def ReattachStory(self):
		self.Story = _GetDbManager().Db.getStory(
			tellername=self.comp.par.Teller.eval(),
			storyname=self.comp.par.Story.eval(),
			check=False)
		self.Teller = self.Story and self.Story.teller

	@property
	def SegmentCount(self):
		return len(self.Story.segments) if self.Story else 0

	def FillTimerSegments(self, dat):
		dat.clear()
		# using '_' prefix to indicate that these columns are custom (not for the timer CHOP)
		dat.appendRow(['length', '_offset_fraction', '_fade_start', '_fade_end'])
		duration = self.segvals['duration']
		fadeinsecs = min(self.comp.par.Fadeintime.eval(), duration)
		fadeoutsecs = min(self.comp.par.Fadeouttime.eval(), duration)
		if duration <= 0 or not self.comp.par.Enablefade or (fadeinsecs <= 0 and fadeoutsecs <= 0):
			dat.appendRow([duration, 0, 1, 1])
		else:
			if (fadeinsecs + fadeoutsecs) > duration:
				fadeoutsecs = duration - fadeinsecs

			def _addSeg(offset, dur, faderange):
				if dur > 0:
					dat.appendRow([dur, offset] + faderange)
					offset += dur / duration
				return offset

			offsetfraction = _addSeg(0, fadeinsecs, [0, 1])
			offsetfraction = _addSeg(offsetfraction, duration - fadeinsecs - fadeoutsecs, [1, 1])
			_addSeg(offsetfraction, fadeoutsecs, [1, 0])

	def GoToSegment(self, index):
		numsegs = self.SegmentCount
		if numsegs == 0:
			return
		index = max(index, 0)
		index = min(index, numsegs - 1)
		# self.LogEvent('Playing segment {}'.format(index))
		self.comp.par.Segmentindex = index
		self.timer.par.start.pulse()

	def OffsetSegmentIndex(self, offset):
		self.GoToSegment(self.comp.par.Segmentindex + offset)

	def GoToRandomSegment(self):
		numsegs = self.SegmentCount
		if numsegs == 0:
			return
		self.GoToSegment(random.randint(0, numsegs - 1))

	def OnSegmentTimerDone(self):
		mode = self.comp.par.Playmode.eval()
		if mode == 'single':
			return
		index = self.comp.par.Segmentindex.eval()
		numsegs = self.SegmentCount
		if mode == 'sequential':
			if index >= numsegs - 1:
				self.GoToSegment(0)
			else:
				self.OffsetSegmentIndex(1)
			self.timer.par.start.pulse()
		elif mode == 'random':
			self.GoToRandomSegment()
			self.timer.par.start.pulse()
