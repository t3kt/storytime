#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include "Settings.h"
#include <memory>

class TrackingProcessor {
public:
  TrackingProcessor(const Settings& settings)
  : _settings(settings) {}

  bool setup();

  bool loadMovie(const std::string& path);

  void close();

  bool processNextFrame();
private:
  const Settings& _settings;
  ofVideoPlayer _video;
  ofxFaceTracker _tracker;
  std::shared_ptr<TrackingOutput> _output;
};

