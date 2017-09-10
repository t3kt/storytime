#pragma once

#include "ofMain.h"
#include "TrackingProcessor.h"
#include "JsonOutput.h"
#include <memory>

class ofApp : public ofBaseApp{

	public:
  ofApp() {}
		void setup();
		void update();
		void draw();

private:

  Settings settings;
  ofVideoPlayer video;
  std::shared_ptr<TrackingProcessor> _processor;
  std::shared_ptr<TrackingOutput> _output;
};

