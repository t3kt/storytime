#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include <set>
#include <iostream>

using Direction = ofxFaceTracker::Direction;
using Feature = ofxFaceTracker::Feature;
using Gesture = ofxFaceTracker::Gesture;

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

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

private:
  void writeHeader();
  ofJson writeFrameObj();

  Settings settings;
  ofVideoPlayer video;
  ofxFaceTracker tracker;
  ofFile dataFile;
  ofJson dataFrames;
};

