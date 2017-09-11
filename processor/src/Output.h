#pragma once

#include "Settings.h"
#include "ofxFaceTracker.h"
#include <memory>

class TrackingOutput {
public:
  static std::shared_ptr<TrackingOutput> createOutput(const OutputSettings& settings);

  TrackingOutput(const OutputSettings& settings)
  : _settings(settings) {}

  virtual bool setup() { return true; }
  virtual void writeSettings(const Settings& settings) {}
  virtual void writeVideoInfo(const ofVideoPlayer& video) {}
  virtual void writeFrame(const ofxFaceTracker& tracker) = 0;
  virtual void save() {}
  virtual void close() {}

protected:
  const OutputSettings& _settings;
};
