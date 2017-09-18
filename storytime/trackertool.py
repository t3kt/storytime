import storytime.animation as anim
from storytime.shared import *
import os.path

def ConvertTrackingTableToAnimation(inputpath, channelspath, keyspath):
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

def TrackingToAnimationSimple(inputpath):
	basepath = os.path.splitext(inputpath)[0]
	channelspath = basepath + '-channels.txt'
	keyspath = basepath + '-keys.txt'
	ConvertTrackingTableToAnimation(
		inputpath,
		channelspath,
		keyspath
	)
