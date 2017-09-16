#include "FrameTableWriter.h"
#include "ofxTEnums.h"

using namespace ofxTCommon;

bool FrameTableWriter::setup() {
  ofLogNotice() << "Opening file " << _filepath << " for frame table output";
  if (!_file.open(_filepath, ofFile::WriteOnly, /*binary*/false) ||
      !_file.canWrite()) {
    ofLogFatalError() << "Cannot open file " << _filepath;
    return false;
  }
  _table = std::make_unique<TableWriter>(_file);
  writeHeaderRow();
  return true;
}

void FrameTableWriter::close() {
  _file.close();
}

void HaarRectangleTableWriter::writeHeaderRow() {
  table().writeCells({
    "frame",
    "found",
    "x",
    "y",
    "w",
    "h",
  });
  table().endRow();
}

void HaarRectangleTableWriter::writeFrame() {
  auto frame = _video.getCurrentFrame();
  table().writeCell(frame);
  if (!_tracker.getHaarFound()) {
    table()
    .writeCell(0)
    .writeBlankCells(4);
  } else {
    table().writeCell(1);
    auto rect = _tracker.getHaarRectangle();
    table()
    .writeCell(rect.getX())
    .writeCell(rect.getY())
    .writeCell(rect.getWidth())
    .writeCell(rect.getHeight());
  }
  table().endRow();
}

void TransformTableWriter::writeHeaderRow() {
  table()
  .writeCells({
    "frame",
    "found",
  })
  .writeHeaderCellsXY("pos_")
  .writeCell("scale")
  .writeHeaderCellsXYZ("orient_")
  .writeCell("dir")
  .writeCells({
    "rot_0_0", "rot_0_1", "rot_0_2", "rot_0_3",
    "rot_1_0", "rot_1_1", "rot_1_2", "rot_1_3",
    "rot_2_0", "rot_2_1", "rot_2_2", "rot_2_3",
    "rot_3_0", "rot_3_1", "rot_3_2", "rot_3_3",
  })
  .endRow();
}

void TransformTableWriter::writeFrame() {
  auto frame = _video.getCurrentFrame();
  table().writeCell(frame);
  if (!_tracker.getFound()) {
    table()
    .writeCell(0)
    .writeBlankCells(2 + 1 + 3 + 1 + 16);
  } else {
    auto pos = _tracker.getPosition();
    auto scale = _tracker.getScale();
    auto orient = _tracker.getOrientation();
    auto dir = _tracker.getDirection();
    auto rot = _tracker.getRotationMatrix();
    table()
    .writeCell(1)
    .writeCells(pos)
    .writeCell(scale)
    .writeCells(orient)
    .writeCell(enumToString(dir))
    .writeCells(rot);
  }
  table().endRow();
}

GestureTableWriter::GestureTableWriter(const ofVideoPlayer& video,
                                       const ofxFaceTracker& tracker,
                                       std::filesystem::path filepath)
: FrameTableWriter(video, tracker, filepath)
, _gestures(getEnumInfo<ofxFaceTracker::Gesture>().values()) {}

void GestureTableWriter::writeHeaderRow() {
  table()
  .writeCell("frame")
  .writeCell("found");

  for (const auto& gesture : _gestures) {
    table().writeCell(enumToString(gesture));
  }

  table().endRow();
}

void GestureTableWriter::writeFrame() {
  auto frame = _video.getCurrentFrame();
  table().writeCell(frame);
  if (!_tracker.getFound()) {
    table()
    .writeCell(0)
    .writeBlankCells(_gestures.size());
  } else {
    table()
    .writeCell(1);
    for (const auto& gesture : _gestures) {
      table().writeCell(_tracker.getGesture(gesture));
    }
  }
  table().endRow();
}


