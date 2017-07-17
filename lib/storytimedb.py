import json
from typing import Dict, List, Optional

class StoryDb:
	def __init__(self, filepath=None):
		self.tellers = {}   # type: Dict[str, 'StoryTeller']
		self.filepath = filepath

	@property
	def enabledTellers(self):
		return _excludeDisabled(self.tellers.values())

	def clear(self):
		self.tellers = {}

	def load(self, filepath=None):
		if filepath:
			self.filepath = filepath
		with open(self.filepath, 'r') as f:
			dbobj = json.load(f)
		self.clear()
		if 'tellers' in dbobj:
			for tname, tobj in dbobj['tellers'].items():
				teller = StoryTeller(tname, obj=tobj)
				self.tellers[tname] = teller

	def save(self):
		dbobj = self.toJson()
		with open(self.filepath, 'w') as f:
			json.dump(dbobj, f, indent='  ')

	def toJson(self):
		return _CleanDict({
			'tellers': _itemDictToJson(self.tellers),
		})

	def addTeller(self, tellername, **kwargs) -> 'StoryTeller':
		if tellername in self.tellers:
			raise Exception('Teller already exists: {0}'.format(tellername))
		teller = self.tellers[tellername] = StoryTeller(tellername, **kwargs)
		return teller

	def addStory(self, tellername, storyname, **kwargs) -> 'Story':
		teller = self.getTeller(tellername, check=True)
		if storyname in teller.stories:
			raise Exception('Story already exists: {0}/{0}'.format(tellername, storyname))
		story = teller.stories[storyname] = Story(storyname, teller, **kwargs)
		return story

	def getTeller(self, tellername, check=False) -> Optional['StoryTeller']:
		teller = self.tellers.get(tellername)
		if check and not teller:
			raise Exception('Teller not found: {0}'.format(tellername))
		return teller

	def getStory(self, tellername, storyname, check=False) -> Optional['Story']:
		teller = self.getTeller(tellername, check=check)
		story = teller and teller.stories.get(storyname)
		if check and not story:
			raise Exception('Story not found: {0}'.format(storyname))
		return story

	def getSegment(self, tellername, storyname, segmentindex) -> Optional['StorySegment']:
		story = self.getStory(tellername, storyname)
		if not story or segmentindex >= len(story.segments):
			return None
		return story.segments[segmentindex]

class StoryTeller:
	def __init__(
			self,
			name,
			label=None,
			stories=None,
			disabled=False,
			obj=None):
		self.name = name
		self.label = label or name
		self.stories = stories or {}  # type: Dict[str, 'Story']
		self.disabled = disabled
		if obj:
			self.label = obj.get('label', self.label)
			self.disabled = obj.get('disabled', self.disabled)
			if 'stories' in obj:
				for sname, sobj in obj['stories'].items():
					self.stories[sname] = Story(sname, self, obj=sobj)

	@property
	def enabledStories(self):
		return _excludeDisabled(self.stories.values())

	def toJson(self):
		return _CleanDict({
			'name': self.name,
			'label': self.label,
			'disabled': self.disabled or None,
			'stories': _itemDictToJson(self.stories),
		})

	def __repr__(self):
		return 'StoryTeller(name={}, label={}, stories={})'.format(
			self.name,
			self.label,
			len(self.stories))

class Story:
	def __init__(
			self,
			name,
			teller: StoryTeller,
			label=None,
			videofile=None,
			subfile=None,
			segments=None,
			enabledranges=None,
			disabled=False,
			obj=None):
		self.name = name
		self.teller = teller
		self.label = name or label
		self.videofile = videofile
		self.subfile = subfile
		self.duration = 0.0
		self.fps = 30
		self.width = 0
		self.height = 0
		self.disabled = disabled
		self.segments = segments or []  # type: List['StorySegment']
		self.enabledranges = enabledranges or []  # type: List['StoryRange']
		if obj:
			self.label = obj.get('label', self.label)
			self.videofile = obj.get('videofile', self.videofile)
			self.subfile = obj.get('subfile', self.subfile)
			self.duration = obj.get('duration', self.duration)
			self.fps = obj.get('fps', self.fps)
			self.width = obj.get('width', self.width)
			self.height = obj.get('height', self.height)
			self.disabled = obj.get('disabled', self.disabled)
			if 'segments' in obj:
				self.segments = [StorySegment(self, obj=sobj) for sobj in obj['segments']]
			if 'enabledranges' in obj:
				self.enabledranges = [StoryRange(self, obj=robj) for robj in obj['enabledranges']]

	def isInEnabledRange(self, segment: 'StorySegment'):
		if not self.enabledranges:
			return True
		return any([r.containsRange(segment) for r in self.enabledranges])

	@property
	def enabledSegments(self):
		if self.enabledranges:
			return [
				segment for segment in self.segments
				if not segment.disabled and self.isInEnabledRange(segment)
			]
		else:
			return _excludeDisabled(self.segments)

	def toJson(self):
		return _CleanDict({
			'name': self.name,
			'label': self.label,
			'videofile': self.videofile,
			'subfile': self.subfile,
			'duration': self.duration,
			'fps': self.fps,
			'width': self.width,
			'height': self.height,
			'disabled': self.disabled or None,
			'segments': _itemListToJson(self.segments),
			'enabledranges': _itemListToJson(self.enabledranges),
		})

	@property
	def aspect(self):
		if self.width == 0 or self.height == 0:
			return 1
		return self.width / self.height

	def __repr__(self):
		return 'Story(name={}, label={}, duration={}, segments={})'.format(
			self.name,
			self.label,
			self.duration,
			len(self.segments))


class StoryTime:
	def __init__(
			self,
			val=None,
			rawval=None):
		self.val = val or 0
		self.rawval = rawval
		raise NotImplemented('INCOMPLETE!!!')

	@classmethod
	def fromValue(cls, val):
		if val is None:
			return None
		if isinstance(val, (float, int)):
			return cls(val=val)
		if isinstance(val, str):
			if val == '':
				return None
			return cls(val=_parseTimeString(val), rawval=val)
		raise Exception('Unsupported time value: {0!r}'.format(val))

def _parseTimeString(s):
	if ':' in s:
		pass
	pass

class StoryRange:
	def __init__(
			self,
			story,
			start=None,
			end=None,
			obj=None):
		self.story = story
		self.start = start or 0
		self.end = end or 0
		if obj:
			self.start = obj.get('start', self.start)
			self.end = obj.get('end', self.end)

	@property
	def duration(self):
		return self.end - self.start

	@property
	def startFraction(self):
		if self.story.duration == 0:
			return 0
		return self.start / self.story.duration

	@property
	def endFraction(self):
		if self.story.duration == 0:
			return 0
		return self.end / self.story.duration

	def containsTime(self, t):
		return self.start <= t <= self.end

	def containsRange(self, r):
		return r.start >= self.start and r.end <= self.end

	def toJson(self):
		return _CleanDict({
			'start': self.start,
			'end': self.end,
		})

	def __repr__(self) -> str:
		return 'StoryRange(start={}, end={})'.format(
			self.start, self.end)


class StorySegment(StoryRange):
	def __init__(
			self,
			story: Story,
			start=None,
			end=None,
			text=None,
			disabled=False,
			obj=None):
		super().__init__(
			story,
			start=start,
			end=end,
			obj=obj)
		self.text = text or ''
		self.disabled = disabled
		if obj:
			self.text = obj.get('text', self.text)
			self.disabled = obj.get('disabled', self.disabled)

	def toJson(self):
		return _MergeDicts(
			super().toJson(),
			_CleanDict({
				'text': self.text,
				'disabled': self.disabled or None,
			})
		)

	def __repr__(self) -> str:
		return 'StorySegment(start={}, end={}, text={})'.format(
			self.start, self.end, self.text)


def _CleanDict(d):
	if not d:
		return None
	for k in list(d.keys()):
		if d[k] is None or d[k] == '' or (isinstance(d[k], list) and len(d[k]) == 0):
			del d[k]
	return d

def _MergeDicts(*parts):
	if parts is None:
		return {}
	d = {}
	for part in parts:
		if part:
			d.update(part)
	return d

def _itemDictToJson(items):
	return {
		itemname: item.toJson()
		for itemname, item in items.items()
	}

def _itemListToJson(items):
	return [item.toJson() for item in items]

def _excludeDisabled(items):
	return [item for item in items if not item.disabled]
