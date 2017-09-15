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
                          const ofxFaceTracker& tracker) override;
  virtual void close() override;
protected:
//  virtual void writeFrameCells(const ofxFaceTracker& tracker) = 0;
  virtual CellList getHeaders() = 0;
  virtual CellList buildFrameCells(const ofVideoPlayer& video,
                                   const ofxFaceTracker& tracker) = 0;

  void writeRow(const CellList& cells);

  TableWriter& table() { return *_table; }

//  void beginRow();
//  void nextCell();
//  void endRow();

  std::filesystem::path _filepath;
  ofFile _file;
  std::unique_ptr<TableWriter> _table;
  bool _atRowStart;
};

class TransformTableWriter
: public FrameTableWriter {
public:
  TransformTableWriter(std::filesystem::path filepath)
  : FrameTableWriter(filepath) {}
protected:
  CellList getHeaders() override;

  CellList buildFrameCells(const ofVideoPlayer& video,
                           const ofxFaceTracker& tracker) override;
};

class HaarRectangleTableWriter
: public FrameTableWriter {
public:
  HaarRectangleTableWriter(std::filesystem::path filepath)
  : FrameTableWriter(filepath) {}
protected:
  CellList getHeaders() override;

  CellList buildFrameCells(const ofVideoPlayer& video,
                           const ofxFaceTracker& tracker) override;
};

template<typename W>
std::shared_ptr<FrameTableWriter> createTableWriter(std::filesystem::path filepath) {
  ofLogNotice() << "Creating table writer for " << filepath;
  return std::make_shared<W>(filepath);
}
