import storytime.animation as anim
from storytime.shared import *
from storytime.tdclip import *
import os.path

def WriteTrackingTableToAnimation(inputpath, channelspath, keyspath):
	with open(inputpath, 'r') as inputfile:
		reader = DATReader(inputfile)
		channels = next(reader)
		if not channels or channels[0] != 'frame':
			raise Exception('Invalid channels, should start with "frame": {}'.format(channels))
		channels = channels[1:]
		anim.WriteChannels(channelspath, channels)
		with anim.AnimationKeysWriter(keyspath, channels) as keyswriter:
			for row in reader:
				frame = int(row[0])
				keyswriter.WriteFrame(frame, row[1:])

def WriteTrackingToAnimationSimple(inputpath):
	basepath = os.path.splitext(inputpath)[0]
	channelspath = basepath + '-channels.txt'
	keyspath = basepath + '-keys.txt'
	WriteTrackingTableToAnimation(
		inputpath,
		channelspath,
		keyspath
	)

def TrackingTableToClip(inputpath, rate=None, start=None, length=None):
	with open(inputpath, 'r') as inputfile:
		reader = DATReader(inputfile)
		channels = next(reader)
		hasframe = channels[0] == 'frame'
		if hasframe:
			channels = channels[1:]
		tracks = []
		for _ in channels:
			tracks.append([])
		for rowindex, rowvals in enumerate(reader):
			if hasframe:
				frame = int(rowvals[0])
				if frame != rowindex:
					message = 'Frame mismatch at line {} (frame: {})'.format(rowindex, frame)
					print('WARNING: ' + message)
					# raise Exception(message)
				rowvals = rowvals[1:]
			for trackindex, val in enumerate(rowvals):
				tracks[trackindex].append(_ParseFloat(val))
		clip = TDClip(rate=rate, start=start, length=length)
		for trackname, vals in zip(channels, tracks):
			clip.AddTrack(trackname, vals)
		return clip

def WriteTrackingToClipSimple(inputpath, rate=None, start=None, length=None):
	basepath = os.path.splitext(inputpath)[0]
	chanpath = basepath + '-chop.clip'
	clip = TrackingTableToClip(inputpath, rate=rate, start=start, length=length)
	clip.WriteToFile(chanpath)

def _ParseFloat(val):
	try:
		return float(val)
	except ValueError:
		return 0
