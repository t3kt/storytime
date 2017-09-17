#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include "TableWriter.h"
#include <memory>
#include <string>
#include <vector>

using CellList = std::vector<std::string>;

class FrameTableWriter : public FrameWriter {
protected:
public:
  FrameTableWriter(const ofVideoPlayer& video,
                   const ofxFaceTracker& tracker,
                   std::filesystem::path filepath)
  : FrameWriter(video, tracker)
  , _filepath(filepath) {}

  virtual ~FrameTableWriter() {
    if (_file.is_open()) {
      _file.close();
    }
  }

  virtual bool setup() override;
  virtual void writeFrame() override = 0;
  virtual void close() override;
protected:
  TableWriter& table() { return *_table; }

  virtual void writeHeaderRow() = 0;

  std::filesystem::path _filepath;
  ofFile _file;
  std::unique_ptr<TableWriter> _table;
  bool _atRowStart;
};

class HaarRectangleTableWriter
: public FrameTableWriter {
public:
  HaarRectangleTableWriter(const ofVideoPlayer& video,
                           const ofxFaceTracker& tracker,
                           std::filesystem::path filepath)
  : FrameTableWriter(video, tracker, filepath) {}
protected:
  void writeHeaderRow() override;

  void writeFrame() override;
};

class TransformTableWriter
: public FrameTableWriter {
public:
  TransformTableWriter(const ofVideoPlayer& video,
                       const ofxFaceTracker& tracker,
                       std::filesystem::path filepath)
  : FrameTableWriter(video, tracker, filepath) {}
protected:
  void writeHeaderRow() override;

  void writeFrame() override;
};

class GestureTableWriter
: public FrameTableWriter {
public:
  GestureTableWriter(const ofVideoPlayer& video,
                     const ofxFaceTracker& tracker,
                     std::filesystem::path filepath);
protected:
  void writeHeaderRow() override;

  void writeFrame() override;
private:
  const std::vector<ofxFaceTracker::Gesture>& _gestures;
};

template<typename W>
std::shared_ptr<FrameTableWriter>
createTableWriter(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker,
                  std::filesystem::path filepath) {
  ofLogNotice() << "Creating table writer for " << filepath;
  return std::make_shared<W>(video, tracker, filepath);
}
