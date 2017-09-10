#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"

ofJson toJson(const ofVec2f& value);

ofJson toJson(const ofVec3f& value);

ofJson toJson(const ofVec4f& value);

ofJson toJson(const glm::vec2& value);

ofJson toJson(const glm::vec3& value);

ofJson toJson(const glm::vec4& value);

ofJson toJson(const ofMatrix4x4& value);

ofJson toJson(const ofRectangle& value);

ofJson toJson(ofxFaceTracker::Direction value);

ofJson toJson(ofxFaceTracker::Feature value);

ofJson toJson(ofxFaceTracker::Gesture value);

ofJson toJson(const ofPolyline& polyline);

class JsonTrackingOutput : public TrackingOutput {
public:
  JsonTrackingOutput(const OutputSettings& settings)
  : TrackingOutput(settings) {}
  bool setup() override;
  void writeVideoInfo(const ofVideoPlayer& video) override;
  void writeFrame(const ofxFaceTracker& tracker) override;
  void save() override;
private:
  ofFile _file;
  ofJson _infoObj;
  ofJson _frameObjs;
};
