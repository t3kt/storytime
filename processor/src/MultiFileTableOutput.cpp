#include "MultiFileTableOutput.h"
#include "FrameTableWriter.h"
#include "JsonOutput.h"
#include "PointsTableWriter.h"

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
    if (!addFrameWriter(createTableWriter<ImagePointsTableWriter>(_video, _tracker, getFilePath("imagepoints.txt")))) {
      return false;
    }
    // TODO: set up points writer
  }

  if (_settings.meshes) {
    // TODO: set up meshes writer
  }

  if (_settings.haarRectangle) {
    if (!addFrameWriter(createTableWriter<HaarRectangleTableWriter>(_video, _tracker, getFilePath("haarrect.txt")))) {
      return false;
    }
  }

  if (_settings.transform) {
    if (!addFrameWriter(createTableWriter<TransformTableWriter>(_video, _tracker, getFilePath("transform.txt")))) {
      return false;
    }
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
    if (!addFrameWriter(createTableWriter<GestureTableWriter>(_video, _tracker, getFilePath("gesture.txt")))) {
      return false;
    }
  }

  return true;
}

bool MultiFileTableOutput::addFrameWriter(std::shared_ptr<FrameWriter> writer) {
  if (!writer->setup()) {
    return false;
  }
  _frameWriters.push_back(writer);
  return true;
}

std::filesystem::path MultiFileTableOutput::getFilePath(const std::filesystem::path& path) const {
  std::filesystem::path dirPath = _dir;
  return dirPath / path;
}

bool MultiFileTableOutput::openWritableFile(const std::filesystem::path& path, ofFile* file) {
  auto filePath = getFilePath(path);
  if (!file->open(filePath, ofFile::WriteOnly, /*binary*/ false) || !file->canWrite()) {
    ofLogFatalError() << "Cannot open file " << filePath;
    return false;
  }
  return true;
}

void MultiFileTableOutput::writeSettings(const Settings& settings) {
  _settingsFile << settings.toJson().dump(2);
  _settingsFile.close();
}

void MultiFileTableOutput::writeVideoInfo() {
  auto infoObj = getVideoInfoJson(_video);
  _videoInfoFile << infoObj.dump(2);
  _videoInfoFile.close();
}

void MultiFileTableOutput::writeFrame() {
  for (auto& writer : _frameWriters) {
    writer->writeFrame();
  }
}

void MultiFileTableOutput::close() {
  for (auto& writer : _frameWriters) {
    writer->close();
  }
}
