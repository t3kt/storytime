#pragma once

#include "FrameTableWriter.h"
#include <string>
#include <vector>

template<typename P>
class PointsTableWriter
: public FrameTableWriter {
public:
  PointsTableWriter(const ofVideoPlayer& video,
                    const ofxFaceTracker& tracker,
                    std::filesystem::path filepath)
  : FrameTableWriter(video, tracker, filepath) {}
protected:
  void writeHeaderRow() override {
    table().writeCells({
      "frame",
      "found",
    });
    //    auto size = _tracker.size();
    auto size = 66;
    auto suffixes = getSuffixes();
    for (auto i = 0; i < size; i++) {
      table().writeHeaderCells("pt" + ofToString(i) + "_", suffixes);
    }
    table().endRow();
  }

  void writeFrame() override {
    auto size = _tracker.size();
    table().writeCell(_video.getCurrentFrame());
    if (!_tracker.getFound()) {
      table().writeCell(0);
      table().writeBlankCells(size * P::DIM);
      return;
    }
    table().writeCell(1);
    for (auto i = 0; i < size; i++) {
      auto point = getPoint(i);
      table().writeCells(point);
    }
    table().endRow();
  }

  virtual std::vector<std::string> getSuffixes() const = 0;
  virtual P getPoint(int i) const = 0;
};

class ImagePointsTableWriter
: public PointsTableWriter<ofVec2f> {
public:
  ImagePointsTableWriter(const ofVideoPlayer& video,
                         const ofxFaceTracker& tracker,
                         std::filesystem::path filepath)
  : PointsTableWriter(video, tracker, filepath) {}

protected:
  ofVec2f getPoint(int i) const override {
    return _tracker.getImagePoint(i);
  }

  std::vector<std::string> getSuffixes() const override {
    return {"x", "y"};
  }
};

class ObjectPointsTableWriter
: public PointsTableWriter<ofVec3f> {
public:
  ObjectPointsTableWriter(const ofVideoPlayer& video,
                          const ofxFaceTracker& tracker,
                          std::filesystem::path filepath)
  : PointsTableWriter(video, tracker, filepath) {}

protected:
  ofVec3f getPoint(int i) const override {
    return _tracker.getObjectPoint(i);
  }

  std::vector<std::string> getSuffixes() const override {
    return {"x", "y", "z"};
  }
};

class MeanObjectPointsTableWriter
: public PointsTableWriter<ofVec3f> {
public:
  MeanObjectPointsTableWriter(const ofVideoPlayer& video,
                              const ofxFaceTracker& tracker,
                              std::filesystem::path filepath)
  : PointsTableWriter(video, tracker, filepath) {}

protected:
  ofVec3f getPoint(int i) const override {
    return _tracker.getMeanObjectPoint(i);
  }

  std::vector<std::string> getSuffixes() const override {
    return {"x", "y", "z"};
  }
};

