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
  JsonTrackingOutput(const ofVideoPlayer& video,
                     const ofxFaceTracker& tracker,
                     const OutputSettings& settings)
  : TrackingOutput(video, tracker)
  , _settings(settings) {}
  bool setup() override;
  void writeSettings(const Settings& settings) override;
  void writeVideoInfo() override;
  void writeFrame() override;
  void close() override;
private:
  const OutputSettings& _settings;
  ofFile _file;
  int _framesSinceFlush;
};
