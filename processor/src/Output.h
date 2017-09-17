#pragma once

#include "Settings.h"
#include "ofVideoPlayer.h"
#include "ofxFaceTracker.h"
#include <memory>

class FrameWriter {
public:
  FrameWriter(const ofVideoPlayer& video,
              const ofxFaceTracker& tracker)
  : _video(video)
  , _tracker(tracker) {}
  virtual ~FrameWriter() {}

  virtual bool setup() { return true; }
  virtual void writeFrame() = 0;
  virtual void close() {}
protected:
  const ofVideoPlayer& _video;
  const ofxFaceTracker& _tracker;
};

class TrackingOutput : public FrameWriter {
public:
  static std::shared_ptr<TrackingOutput>
  createOutput(const ofVideoPlayer& video,
               const ofxFaceTracker& tracker,
               const OutputSettings& settings);

  TrackingOutput(const ofVideoPlayer& video,
                 const ofxFaceTracker& tracker)
  : FrameWriter(video, tracker) {}

  virtual void writeSettings(const Settings& settings) {}
  virtual void writeVideoInfo() {}
};
