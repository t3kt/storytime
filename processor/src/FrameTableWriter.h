#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include <memory>
#include <string>
#include <vector>

class FrameTableWriter : public FrameWriter {
protected:
  using CellList = std::vector<std::string>;
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

//  void beginRow();
//  void nextCell();
//  void endRow();

  std::filesystem::path _filepath;
  ofFile _file;
  bool _atRowStart;
};

namespace CreateTableWriter {
  std::shared_ptr<FrameTableWriter> haarRectangle(std::filesystem::path filepath);
}
