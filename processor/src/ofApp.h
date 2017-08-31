#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"

class ofApp : public ofBaseApp{

	public:
		void setup();
		void update();
		void draw();

private:
  void writeHeader();
  ofJson writeFrameObj();

  ofVideoPlayer video;
  ofxFaceTracker tracker;
  ofFile dataFile;
  ofJson dataFrames;
};
