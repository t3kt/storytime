#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"

namespace ofxTCommon {
  namespace JsonUtil {
    ofJson toJson(const ofPolyline& polyline);
  }
}

ofJson getVideoInfoJson(const ofVideoPlayer& video);

class JsonTrackingOutput : public TrackingOutput {
public:
  JsonTrackingOutput(const OutputSettings& settings)
  : _settings(settings) {}
  bool setup() override;
  void writeSettings(const Settings& settings) override;
  void writeVideoInfo(const ofVideoPlayer& video) override;
  void writeFrame(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker) override;
  void close() override;
private:
  const OutputSettings& _settings;
  ofFile _file;
  int _framesSinceFlush;
};
