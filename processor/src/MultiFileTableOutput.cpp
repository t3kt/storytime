#include "MultiFileTableOutput.h"
#include "FrameTableWriter.h"
#include "JsonOutput.h"
#include "PointsTableWriter.h"
#include "ExposedFaceTracker.h"
#include <ofxTEnums.h>

using namespace ofxTCommon;

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
  if (!openWritableFile("videoinfo.txt", &_videoInfoFile)) {
    return false;
  }
  if (_settings.featureIndices) {
    if (!writeFeatureIndices()) {
      return false;
    }
  }

  if (_settings.imagePoints) {
    if (!addFrameWriter(createTableWriter<ImagePointsTableWriter>(_video, _tracker, getFilePath("imagepoints.txt")))) {
      return false;
    }
  }
  if (_settings.objectPoints) {
    if (!addFrameWriter(createTableWriter<ObjectPointsTableWriter>(_video, _tracker, getFilePath("objectpoints.txt")))) {
      return false;
    }
  }
  if (_settings.meanObjectPoints) {
    if (!addFrameWriter(createTableWriter<MeanObjectPointsTableWriter>(_video, _tracker, getFilePath("meanobjectpoints.txt")))) {
      return false;
    }
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

bool MultiFileTableOutput::writeFeatureIndices() {
  ofFile file;
  if (!openWritableFile("featureindices.json", &file)) {
    return false;
  }
  ofJson obj = {};
  for (auto feature : getEnumInfo<ofxFaceTracker::Feature>().values()) {
    obj[enumToString(feature)] = ExposedFaceTracker::getFeatureIndices(feature);
  }
  file << obj.dump(2);
  file.close();
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
  TableWriter table(_videoInfoFile);
  table
  .writeCell("file")
  .writeCell(_video.getMoviePath())
  .endRow();

  table
  .writeCell("width")
  .writeCell(_video.getWidth())
  .endRow();

  table
  .writeCell("height")
  .writeCell(_video.getHeight())
  .endRow();

  table
  .writeCell("frameCount")
  .writeCell(_video.getTotalNumFrames())
  .endRow();

  table
  .writeCell("duration")
  .writeCell(_video.getDuration())
  .endRow();

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
