#include "ofMain.h"
#include "ofApp.h"
#include <iostream>
#include <string>
#include "Settings.h"
#include "TrackingProcessor.h"
#include "ofJson.h"

int usage(const char* cmd);

bool loadSettingsFile(const std::string& path, Settings* settings) {
  ofLogNotice() << "Loading settings from file '" << path << "'";
  ofFile file;
  if (!file.openFromCWD(path,
                        ofFile::ReadOnly,
                        /*binary=*/ false)) {
    return false;
  }
  if (!file.exists()) {
    return false;
  }
  ofJson obj;

  try{
    file >> obj;
  }catch(std::exception & e){
    ofLogFatalError("ofLoadJson") << "Error loading json from " << file.path() << ": " << e.what();
    return false;
  }catch(...){
    ofLogFatalError("ofLoadJson") << "Error loading json from " << file.path();
    return false;
  }

  settings->readJson(obj);

  return true;
}

int main(int argc, const char **argv){
//	ofSetupOpenGL(1024,768,OF_WINDOW);			// <-------- setup the GL context
//
//	// this kicks off the running of my app
//	// can be OF_WINDOW or OF_FULLSCREEN
//	// pass in width and height too:
//	ofRunApp(new ofApp());


  // DEBUG STUFF !!!!!!!!!

  const char* DEBUG_ARGV[] = {
    "DBG-COMMAND",
    "/Users/tekt/creations/storytime/processor/testing/settings.json",
    "/Users/tekt/creations/storytime/processor/testing/career-advice.mp4",
    "/Users/tekt/creations/storytime/processor/testing/output.json",
  };
  argv = DEBUG_ARGV;

  // END DEBUG STUFF!!!!!!!


  if (argc < 3) {
    return usage(argv[0]);
  }

  Settings settings;
  std::string settingsPath = argv[1];
  if (!loadSettingsFile(settingsPath, &settings)) {
    ofLogFatalError() << "Failed to open settings file '" << settingsPath << "'!";
    return 1;
  }

  std::string videoPath = argv[2];

  if (argc > 2) {
    settings.output.file = argv[3];
  }

  if (argc > 3) {
    return usage(argv[0]);
  }

  ofLogNotice() << "Settings:\n" << settings.toJson().dump(2);
  ofLogNotice() << "Video file: " << videoPath;
  ofLogNotice() << "Output file: " << settings.output.file;
  return 0;
  TrackingProcessor processor(settings);
  if (!processor.setup()) {
    ofLogFatalError() << "Error during tracking processor setup!";
    return 1;
  }
  if (!processor.loadMovie(videoPath)) {
    ofLogFatalError() << "Error loading video!";
    return 1;
  }

  for (;;) {
    ofLogVerbose() << "Processing next frame..";
    if (!processor.processNextFrame()) {
      ofLogNotice() << "Finished processing frames";
      break;
    }
  }
  processor.close();
  ofLogNotice() << "Finished!";
  return 0;
}

int usage(const char* cmd) {
  std::cout << "Usage: " << cmd << " <settings-path.json> <video-file.mp4> [output-path.json]" << std::endl;
  return 1;
}
