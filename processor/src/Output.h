#pragma once

#include "Settings.h"
#include "ofxFaceTracker.h"
#include <memory>

class FrameWriter {
public:
  virtual ~FrameWriter() {}

  virtual bool setup() { return true; }
  virtual void writeFrame(const ofxFaceTracker& tracker) = 0;
  virtual void close() {}
};

class TrackingOutput : public FrameWriter {
public:
  static std::shared_ptr<TrackingOutput> createOutput(const OutputSettings& settings);

  virtual void writeSettings(const Settings& settings) {}
  virtual void writeVideoInfo(const ofVideoPlayer& video) {}
};
