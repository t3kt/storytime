#pragma once

#include <ofJson.h>
#include "ofxTJsonIO.h"
#include "ofxFaceTracker.h"

using Direction = ofxFaceTracker::Direction;
using Feature = ofxFaceTracker::Feature;
using Gesture = ofxFaceTracker::Gesture;

class TrackerFrameData : public ofxTCommon::JsonWritable {
public:

};

