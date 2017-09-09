#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include <memory>

class Settings {
public:
  bool includePoints;
  bool includeMeshes;
  bool includeHaarRectangle;
  bool includeTransform;
  bool includeDirection;
  bool includeFeatures;
  bool includeGestures;
};

class TrackingOutput {
public:
  virtual void setup(const Settings& settings) {
    _settings = settings;
  }
  virtual bool writeFrame(const ofxFaceTracker& tracker) = 0;
  virtual void close() {}

protected:
  Settings _settings;
};



class TrackingProcessor {
public:
  void setup(const Settings& settings,
             std::shared_ptr<TrackingOutput> output);

  bool loadMovie(const std::string& path) {
    return _video.load(path);
  }

  void close();

  bool processNextFrame();
private:
  ofVideoPlayer _video;
  ofxFaceTracker _tracker;
  std::shared_ptr<TrackingOutput> _output;
};

