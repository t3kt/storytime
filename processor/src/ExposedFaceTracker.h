#pragma once

#include "ofxFaceTracker.h"

class ExposedFaceTracker : public ofxFaceTracker {
public:
  static std::vector<int> getFeatureIndices(Feature feature) {
    return ofxFaceTracker::getFeatureIndices(feature);
  }
};
