import json
from typing import Dict, List, Optional

class StoryDb:
	def __init__(self, filepath=None):
		self.tellers = {}   # type: Dict[str, 'StoryTeller']
		self.filepath = filepath

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
		story = teller.stories[storyname] = Story(storyname, **kwargs)
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
			obj=None):
		self.name = name
		self.label = label or name
		self.stories = stories or {}  # type: Dict[str, 'Story']
		if obj:
			self.label = obj.get('label', self.label)
			if 'stories' in obj:
				for sname, sobj in obj['stories'].items():
					self.stories[sname] = Story(sname, obj=sobj)

	def toJson(self):
		return _CleanDict({
			'name': self.name,
			'label': self.label,
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
			label=None,
			videofile=None,
			subfile=None,
			segments=None,
			obj=None):
		self.name = name
		self.label = name or label
		self.videofile = videofile
		self.subfile = subfile
		self.duration = 0.0
		self.fps = 30
		self.width = 0
		self.height = 0
		self.segments = segments or []  # type: List['StorySegment']
		if obj:
			self.label = obj.get('label', self.label)
			self.videofile = obj.get('videofile', self.videofile)
			self.subfile = obj.get('subfile', self.subfile)
			self.duration = obj.get('duration', self.duration)
			self.fps = obj.get('fps', self.fps)
			self.width = obj.get('width', self.width)
			self.height = obj.get('height', self.height)
			if 'segments' in obj:
				self.segments = [StorySegment(obj=sobj) for sobj in obj['segments']]

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
			'segments': _itemListToJson(self.segments)
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

class StorySegment:
	def __init__(
			self,
			start=None,
			end=None,
			text=None,
			obj=None):
		self.start = start or 0
		self.end = end or 0
		self.text = text or ''
		if obj:
			self.start = obj.get('start', self.start)
			self.end = obj.get('end', self.end)
			self.text = obj.get('text', self.text)

	@property
	def duration(self):
		return self.end - self.start

	def toJson(self):
		return _CleanDict({
			'start': self.start,
			'end': self.end,
			'text': self.text,
		})

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

def _itemDictToJson(items):
	return {
		itemname: item.toJson()
		for itemname, item in items.items()
	}

def _itemListToJson(items):
	return [item.toJson() for item in items]
