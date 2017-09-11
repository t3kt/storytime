#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include "Settings.h"
#include <memory>

class TrackingProcessor {
public:
  bool setup(Settings settings);

  bool loadMovie(const std::string& path);

  bool processNextFrame();

  void close();

  ofVideoPlayer& video() { return _video; }
  ofxFaceTracker& tracker() { return _tracker; }
private:
  Settings _settings;
  ofVideoPlayer _video;
  ofxFaceTracker _tracker;
  std::shared_ptr<TrackingOutput> _output;
};

