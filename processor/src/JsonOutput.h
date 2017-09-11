#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"

namespace ofxTCommon {
  namespace JsonUtil {
    ofJson toJson(const ofPolyline& polyline);
  }
}

class JsonTrackingOutput : public TrackingOutput {
public:
  JsonTrackingOutput(const OutputSettings& settings)
  : TrackingOutput(settings) {}
  bool setup() override;
  void writeVideoInfo(const ofVideoPlayer& video) override;
  void writeFrame(const ofxFaceTracker& tracker) override;
  void close() override;
private:
  ofFile _file;
};
