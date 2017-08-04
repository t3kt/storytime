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

	def saveDb(self):
		self.db.save()

	def addTeller(self, args):
		tellername = args.teller
		self.db.addTeller(tellername, label=args.label)

	def addStory(self, args):
		tellername = args.teller
		storyname = args.story
		self.db.addStory(
			tellername,
			storyname,
			label=args.label,
			videofile=args.vidfile,
			subfile=args.subfile,
		)
		if args.vidfile:
			self.loadStoryVideo(tellername, storyname, args.vidfile)
		if args.subfile:
			self.loadStorySubtitles(tellername, storyname, args.subfile)

	def reloadSubtitles(self, args):
		self.loadStorySubtitles(
			args.teller,
			args.story,
			args.subfile,
		)

	def loadStorySubtitles(self, tellername, storyname, subfile=None):
		story = self.db.getStory(tellername, storyname, check=True)
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

	def loadStoryVideo(self, tellername, storyname, videofile=None):
		story = self.db.getStory(tellername, storyname, check=True)
		if videofile:
			story.videofile = videofile
		video = VideoFileClip(story.videofile)
		story.duration = video.duration
		story.fps = video.fps

	def performAction(self, action, args):
		if action == 'addteller':
			self.addTeller(args)
		elif action == 'addstory':
			self.addStory(args)
		elif action == 'reloadsub':
			self.reloadSubtitles(args)
		else:
			raise Exception('Unsupported action: {0}'.format(action))

def main():
	parser = argparse.ArgumentParser(description='manipulate storytime database')
	parser.add_argument(
		'dbfile', metavar='DB', type=str,
		help='Database file path')
	parser.add_argument(
		'action', metavar='A', type=str,
		choices=['addteller', 'addstory', 'rewrite', 'reloadsub'],
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
