from storytime.storytimedb import *
import pysrt
from moviepy.editor import VideoFileClip
import argparse
import os.path

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

	def performAction(self, action, args):
		if action == 'addteller':
			self.addTeller(args)
		elif action == 'addstory':
			self.addStory(args)
		elif action == 'reloadsub':
			self.loadStorySubtitles(self._getStories(args), args.subfile)
		elif action == 'reloadvid':
			self.loadStoryVideo(self._getStories(args), args.vidfile)
		else:
			raise Exception('Unsupported action: {0}'.format(action))

def main():
	parser = argparse.ArgumentParser(description='manipulate storytime database')
	parser.add_argument(
		'dbfile', metavar='DB', type=str,
		help='Database file path')
	parser.add_argument(
		'action', metavar='A', type=str,
		choices=['addteller', 'addstory', 'rewrite', 'reloadsub', 'reloadvid'],
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

	tool.saveDb()

if __name__ == '__main__':
	main()
