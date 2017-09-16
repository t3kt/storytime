#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){
  if (!_processor.setup(_settings)) {
    ofLogFatalError() << "Error during tracking processor setup!";
    exit();
    return;
  }
  if (!_processor.loadMovie(_videoPath)) {
    ofLogFatalError() << "Error loading video: " << _videoPath << "!";
    exit();
    return;
  }
}

//--------------------------------------------------------------
void ofApp::update() {

  ofLogVerbose() << "Processing next frame..";
  if (!_processor.processNextFrame()) {
    ofLogNotice() << "Finished processing frames";
    exit();
    return;
  }
}

//--------------------------------------------------------------
void ofApp::draw(){
  auto& video = _processor.video();
  auto& tracker = _processor.tracker();

  float scale = ofGetWidth() / video.getWidth();
  ofScale(scale, scale);
  video.draw(0, 0);
  ofSetLineWidth(2);
  tracker.draw(true);
  ofDrawBitmapString(ofToString((int) ofGetFrameRate()), 10, 20);
}
