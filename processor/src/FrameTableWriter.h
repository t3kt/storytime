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
  FrameTableWriter(std::filesystem::path filepath)
  : _filepath(filepath) {}

  virtual ~FrameTableWriter() {
    if (_file.is_open()) {
      _file.close();
    }
  }

  virtual bool setup() override;
  virtual void writeFrame(const ofVideoPlayer& video,
                          const ofxFaceTracker& tracker) override = 0;
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
  HaarRectangleTableWriter(std::filesystem::path filepath)
  : FrameTableWriter(filepath) {}
protected:
  void writeHeaderRow() override;

  void writeFrame(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker) override;
};

class TransformTableWriter
: public FrameTableWriter {
public:
  TransformTableWriter(std::filesystem::path filepath)
  : FrameTableWriter(filepath) {}
protected:
  void writeHeaderRow() override;

  void writeFrame(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker) override;
};

class GestureTableWriter
: public FrameTableWriter {
public:
  GestureTableWriter(std::filesystem::path filepath);
protected:
  void writeHeaderRow() override;

  void writeFrame(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker) override;
private:
  const std::vector<ofxFaceTracker::Gesture>& _gestures;
};

template<typename W>
std::shared_ptr<FrameTableWriter> createTableWriter(std::filesystem::path filepath) {
  ofLogNotice() << "Creating table writer for " << filepath;
  return std::make_shared<W>(filepath);
}
