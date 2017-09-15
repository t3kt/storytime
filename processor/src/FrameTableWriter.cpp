#include "FrameTableWriter.h"

bool FrameTableWriter::setup() {
  ofLogNotice() << "Opening file " << _filepath << " for frame table output";
  if (!_file.open(_filepath, ofFile::WriteOnly, /*binary*/false) ||
      !_file.canWrite()) {
    ofLogFatalError() << "Cannot open file " << _filepath;
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

void FrameTableWriter::writeFrame(const ofVideoPlayer& video,
                                  const ofxFaceTracker& tracker) {
  auto cells = buildFrameCells(video, tracker);
  writeRow(cells);
}

class HaarRectangleTableWriter
: public FrameTableWriter {
public:
  HaarRectangleTableWriter(std::filesystem::path filepath)
  : FrameTableWriter(filepath) {}
protected:
  CellList getHeaders() override {
    return {
      "frame",
      "found",
      "x",
      "y",
      "w",
      "h",
    };
  }

  CellList buildFrameCells(const ofVideoPlayer& video,
                           const ofxFaceTracker& tracker) override {
    auto frame = video.getCurrentFrame();
    if (!tracker.getHaarFound()) {
      return {
        ofToString(frame),
        "0",
        "",
        "",
        "",
        "",
      };
    }
    auto rect = tracker.getHaarRectangle();
    return {
      ofToString(frame),
      "1",
      ofToString(rect.getX()),
      ofToString(rect.getY()),
      ofToString(rect.getWidth()),
      ofToString(rect.getHeight()),
    };
  }
};

std::shared_ptr<FrameTableWriter>
CreateTableWriter::haarRectangle(std::filesystem::path filepath) {
  ofLogNotice() << "Creating table writer [haar rect] for " << filepath;
  return std::make_shared<HaarRectangleTableWriter>(filepath);
}
