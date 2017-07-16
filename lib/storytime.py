try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

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
