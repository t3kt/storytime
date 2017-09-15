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

void HaarRectangleTableWriter::writeFrame(const ofVideoPlayer& video,
                         const ofxFaceTracker& tracker) {
  auto frame = video.getCurrentFrame();
  table().writeCell(frame);
  if (!tracker.getHaarFound()) {
    table()
    .writeCell(0)
    .writeBlankCells(4);
  } else {
    table().writeCell(1);
    auto rect = tracker.getHaarRectangle();
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

    "pos_x", "pos_y",

    "scale",

    "orient_x", "orient_y", "orient_z",

    "dir",

    "rot_0_0", "rot_0_1", "rot_0_2", "rot_0_3",
    "rot_1_0", "rot_1_1", "rot_1_2", "rot_1_3",
    "rot_2_0", "rot_2_1", "rot_2_2", "rot_2_3",
    "rot_3_0", "rot_3_1", "rot_3_2", "rot_3_3",
  })
  .endRow();
}

void TransformTableWriter::writeFrame(const ofVideoPlayer& video,
                                               const ofxFaceTracker& tracker) {
  auto frame = video.getCurrentFrame();
  table().writeCell(frame);
  if (!tracker.getFound()) {
    table()
    .writeCell(0)
    .writeBlankCells(2 + 1 + 3 + 1 + 16);
  } else {
    auto pos = tracker.getPosition();
    auto scale = tracker.getScale();
    auto orient = tracker.getOrientation();
    auto dir = tracker.getDirection();
    auto rot = tracker.getRotationMatrix();
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


