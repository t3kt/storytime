#pragma once

#include "ofMain.h"
#include "TrackingProcessor.h"

class ofApp : public ofBaseApp {
public:
  ofApp(Settings settings, std::string videoPath)
  : _settings(settings)
  , _videoPath(videoPath) {}

  void setup();
  void update();
  void draw();

private:
  std::string _videoPath;
  Settings _settings;
  TrackingProcessor _processor;
};

