#include "MultiFileTableOutput.h"


bool MultiFileTableOutput::setup() {
  _dir.openFromCWD(_settings.file);
  if (!_dir.exists()) {
    if (!_dir.create(/*recursive*/ true)) {
      return false;
    }
  } else {
    if (!_dir.isDirectory()) {
      return false;
    }
  }
  if (!openWritableFile("settings.json", &_settingsFile)) {
    return false;
  }
  if (!openWritableFile("videoinfo.json", &_videoInfoFile)) {
    return false;
  }

  // TODO: set up table writers!
  return true;
}

bool MultiFileTableOutput::openWritableFile(const std::filesystem::path& path, ofFile* file) {
  std::filesystem::path dirPath = _dir;
  auto filePath = dirPath / path;
  if (!file->open(filePath, ofFile::WriteOnly, /*binary*/ false) || !file->canWrite()) {
    ofLogFatalError() << "Cannot open file " << filePath;
    return false;
  }
}

void MultiFileTableOutput::writeSettings(const Settings& settings) {
  _settingsFile << settings.toJson().dump(2);
  _settingsFile.close();
}

void MultiFileTableOutput::writeVideoInfo(const ofVideoPlayer& video) {
  auto infoObj = getVideoInfoJson(video);
  _videoInfoFile << infoObj.dump(2);
  _videoInfoFile.close();
}

void MultiFileTableOutput::writeFrame(const ofxFaceTracker& tracker) {
  // TODO: frame output!
}

void MultiFileTableOutput::close() {
  // TODO: close!
}
