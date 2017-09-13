#include "FrameTableWriter.h"

bool FrameTableWriter::setup() {
  if (!_file.canWrite()) {
    return false;
  }
  writeHeaders();
  return true;
}

void FrameTableWriter::close() {
  _file.close();
}

const char CELL_SEPARATOR = '\t';
const char LINE_SEPARATOR = '\n';

void FrameTableWriter::writeRow(const std::vector<std::string>& cells) {
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
}

void FrameTableWriter::writeFrame(const ofxFaceTracker& tracker) {
  auto cells = buildFrameCells(tracker);
  writeRow(cells);
}
