#include "FrameTableWriter.h"

bool FrameTableWriter::setup() {
  if (!_file.canWrite()) {
    return false;
  }
  auto headers = getHeaders();
  writeRow(headers);
  return true;
}

void FrameTableWriter::close() {
  _file.close();
}

const char CELL_SEPARATOR = '\t';
const char LINE_SEPARATOR = '\n';

void FrameTableWriter::writeRow(const CellList& cells) {
  bool atStart = true;
  for (const auto& cell : cells) {
    if (atStart) {
      atStart = false;
    } else {
      _file << CELL_SEPARATOR;
    }
    _file << cell;
  }
  _file << LINE_SEPARATOR;
  _file.flush();
}

void FrameTableWriter::writeFrame(const ofxFaceTracker& tracker) {
  auto cells = buildFrameCells(tracker);
  writeRow(cells);
}

class HaarRectangleTableWriter
: public FrameTableWriter {
public:
  HaarRectangleTableWriter(ofFile file)
  : FrameTableWriter(file) {}
protected:
  CellList getHeaders() override {
    return {
      "x",
      "y",
      "w",
      "h",
    };
  }

  CellList buildFrameCells(const ofxFaceTracker& tracker) override {
    if (!tracker.getHaarFound()) {
      return {
        "",
        "",
        "",
        "",
      };
    }
    auto rect = tracker.getHaarRectangle();
    return {
      ofToString(rect.getX()),
      ofToString(rect.getY()),
      ofToString(rect.getWidth()),
      ofToString(rect.getHeight()),
    };
  }
};

std::shared_ptr<FrameTableWriter>
CreateTableWriter::haarRectangle(ofFile file) {
  return std::make_shared<HaarRectangleTableWriter>(file);
}
