#include "ofMain.h"
#include "ofApp.h"
#include "ofAppGLFWWindow.h"
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
  ofAppGLFWWindow window;
	ofSetupOpenGL(&window, 1024, 768, OF_WINDOW);

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

  if (argc > 3) {
    settings.output.file = argv[3];
  }

  if (argc > 4) {
    return usage(argv[0]);
  }

  ofLogNotice() << "Settings:\n" << settings.toJson().dump(2);
  ofLogNotice() << "Video file: " << videoPath;
  ofLogNotice() << "Output file: " << settings.output.file;

  ofRunApp(new ofApp(settings, videoPath));

  return 0;
}

int usage(const char* cmd) {
  std::cout << "Usage: " << cmd << " <settings-path.json> <video-file.mp4> [output-path.json]" << std::endl;
  return 1;
}
