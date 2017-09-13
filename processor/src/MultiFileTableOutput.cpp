#include "MultiFileTableOutput.h"
#include "JsonOutput.h"

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

  if (_settings.points) {
    // TODO: set up points writer
  }

  if (_settings.meshes) {
    // TODO: set up meshes writer
  }

  if (_settings.haarRectangle) {
    // TODO: set up haar rectangle writer
  }

  if (_settings.transform) {
    // TODO: set up transform / direction writer
  }

  if (_settings.imageFeatures) {
    // TODO: set up image features writer
  }

  if (_settings.objectFeatures) {
    // TODO: set up object features writer
  }

  if (_settings.meanObjectFeatures) {
    // TODO: set up mean object features writer
  }

  if (_settings.gestures) {
    // TODO: set up gestures writer
  }

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
  for (auto& writer : _frameWriters) {
    writer->writeFrame(tracker);
  }
}

void MultiFileTableOutput::close() {
  for (auto& writer : _frameWriters) {
    writer->close();
  }
}
