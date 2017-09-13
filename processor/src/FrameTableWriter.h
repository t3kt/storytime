#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include <string>
#include <vector>

class FrameTableWriter : public FrameWriter {
public:
  FrameTableWriter(ofFile file)
  : _file(file) {}
  virtual bool setup() override;
  virtual void writeFrame(const ofxFaceTracker& tracker) override;
  virtual void close() override;
protected:
//  virtual void writeFrameCells(const ofxFaceTracker& tracker) = 0;
  virtual void writeHeaders() = 0;
  virtual std::vector<std::string> buildFrameCells(const ofxFaceTracker& tracker) = 0;

  void writeRow(const std::vector<std::string>& cells);

//  void beginRow();
//  void nextCell();
//  void endRow();

  ofFile _file;
  bool _atRowStart;
};
