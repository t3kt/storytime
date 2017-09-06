from storytime.storytimedb import *
import pysrt
from moviepy.editor import VideoFileClip
import argparse
import os.path
import csv
import re

def _initCsvDATDialect():
	if 'DAT' not in csv.list_dialects():
		csv.register_dialect(
			'DAT',
			delimiter='\t',
			doublequote=False,
			escapechar='',
			lineterminator='\n',
			quoting=csv.QUOTE_NONE)

def _cleanValueForDAT(val):
	if val and isinstance(val, str):
		val = re.sub('[\t\n ]+', ' ', val)
		return val.replace('"', '')
	return val

def _cleanDictForDAT(obj):
	if not obj:
		return {}
	return {
		key: _cleanValueForDAT(val)
		for key, val in obj.items()
	}

class StorytimeTool:
	def __init__(self, dbfile):
		self.db = StoryDb(dbfile)
		if os.path.exists(dbfile):
			self.db.load()
		else:
			print('DB file not found, creating empty DB: {0}'.format(dbfile))

	def reloadDb(self, dbfile=None):
		self.db.load(filepath=dbfile)

	def saveDb(self):
		self.db.save()

	def addTeller(self, args):
		tellername = args.teller
		self.db.addTeller(tellername, label=args.label)

	def addStory(self, args):
		tellername = args.teller
		storyname = args.story
		story = self.db.addStory(
			tellername,
			storyname,
			label=args.label,
			videofile=args.vidfile,
			subfile=args.subfile,
		)
		if args.vidfile:
			self.loadStoryVideo([story], args.vidfile)
		if args.subfile:
			self.loadStorySubtitles([story], args.subfile)

	@staticmethod
	def loadStorySubtitles(stories, subfile=None):
		if subfile and len(stories) > 1:
			raise Exception('Cannot apply the same sub file to {} stories!'.format(len(stories)))
		for story in stories:
			if subfile:
				story.subfile = subfile
			subs = pysrt.open(story.subfile)
			story.segments = [
				StorySegment(
					story,
					start=item.start.ordinal / 1000,
					end=item.end.ordinal / 1000,
					text=item.text_without_tags
				)
				for item in subs
			]

	@staticmethod
	def loadStoryVideo(stories, vidfile=None):
		if vidfile and len(stories) > 1:
			raise Exception('Cannot apply the same video file to {} stories!'.format(len(stories)))
		for story in stories:
			if vidfile:
				story.videofile = vidfile
			video = VideoFileClip(story.videofile)
			story.duration = video.duration
			story.fps = video.fps
			story.width = video.w
			story.height = video.h

	def _getStories(self, args):
		if args.teller == 'all':
			return list(self.db.allStories)
		if args.story == 'all':
			return list(self.db.getTeller(args.teller, check=True).stories.values())
		return [self.db.getStory(args.teller, args.story, check=True)]

	def writeTellerTable(self, outpath=None):
		_initCsvDATDialect()
		outpath = outpath or 'data/_tables/tellers.txt'
		with open(outpath, 'w') as datfile:
			writer = csv.DictWriter(datfile, ['name', 'label', 'storycount'], dialect='DAT')
			writer.writeheader()
			for teller in self.db.tellers.values():
				if teller.disabled:
					continue
				writer.writerow(_cleanDictForDAT({
					'name': teller.name,
					'label': teller.label,
					'storycount': len(teller.stories),
				}))

	def writeStoryTable(self, outpath=None):
		_initCsvDATDialect()
		outpath = outpath or 'data/_tables/stories.txt'
		with open(outpath, 'w') as datfile:
			writer = csv.DictWriter(
				datfile,
				['id', 'teller', 'story', 'label', 'duration', 'fps', 'width', 'height', 'segmentcount', 'vidfile'],
				dialect='DAT')
			writer.writeheader()
			for teller in self.db.tellers.values():
				if teller.disabled:
					continue
				for story in teller.stories.values():
					if story.disabled:
						continue
					writer.writerow(_cleanDictForDAT({
						'id': '{0}/{1}'.format(teller.name, story.name),
						'teller': teller.name,
						'story': story.name,
						'label': story.label,
						'duration': story.duration,
						'fps': story.fps,
						'segmentcount': len(story.enabledSegments),
						'vidfile': story.videofile,
						'width': int(story.width),
						'height': int(story.height),
					}))

	def writeSegmentTable(self, outpath=None):
		_initCsvDATDialect()
		outpath = outpath or 'data/_tables/segments.txt'
		with open(outpath, 'w') as datfile:
			writer = csv.DictWriter(
				datfile,
				[
					'id', 'teller', 'story', 'index',
					'start', 'end', 'duration',
					'start_fraction', 'end_fraction',
					'text',
				],
				dialect='DAT')
			writer.writeheader()
			for teller in self.db.tellers.values():
				if teller.disabled:
					continue
				for story in teller.stories.values():
					if story.disabled:
						continue
					for index, segment in enumerate(story.enabledSegments):
						writer.writerow(_cleanDictForDAT({
							'id': '{0}/{1}/{2}'.format(teller.name, story.name, index),
							'teller': teller.name,
							'story': story.name,
							'index': index,
							'start': segment.start,
							'end': segment.end,
							'start_fraction': segment.startFraction,
							'end_fraction': segment.endFraction,
							'duration': segment.duration,
							'text': segment.text,
						}))

	def writeTables(self, tellerspath=None, storiespath=None, segmentspath=None):
		self.writeTellerTable(outpath=tellerspath)
		self.writeStoryTable(outpath=storiespath)
		self.writeSegmentTable(outpath=segmentspath)

	def performAction(self, action, args):
		if action == 'addteller':
			self.addTeller(args)
		elif action == 'addstory':
			self.addStory(args)
		elif action == 'reloadsub':
			self.loadStorySubtitles(self._getStories(args), args.subfile)
		elif action == 'reloadvid':
			self.loadStoryVideo(self._getStories(args), args.vidfile)
		elif action == 'writetables':
			self.writeTables()
		else:
			raise Exception('Unsupported action: {0}'.format(action))

def main():
	parser = argparse.ArgumentParser(description='manipulate storytime database')
	parser.add_argument(
		'dbfile', metavar='DB', type=str,
		help='Database file path')
	parser.add_argument(
		'action', metavar='A', type=str,
		choices=['addteller', 'addstory', 'rewrite', 'reloadsub', 'reloadvid', 'writetables'],
		help='Database action')
	parser.add_argument(
		'-t', '--teller', metavar='T', type=str,
		help='Teller name')
	parser.add_argument(
		'-s', '--story', type=str,
		help='Story name')
	parser.add_argument(
		'-l', '--label', type=str,
		help='Label for target item')
	parser.add_argument(
		'--vidfile', type=str,
		help='Video file path')
	parser.add_argument(
		'--subfile', type=str,
		help='Subtitle file path')
	args = parser.parse_args()
	tool = StorytimeTool(args.dbfile)

	if args.action != 'rewrite':
		tool.performAction(args.action, args)

	if args.action != 'writetables':
		tool.saveDb()

if __name__ == '__main__':
	main()
