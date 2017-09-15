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

CellList HaarRectangleTableWriter::getHeaders() {
  return {
    "frame",
    "found",
    "x",
    "y",
    "w",
    "h",
  };
}

CellList HaarRectangleTableWriter::buildFrameCells(const ofVideoPlayer& video,
                         const ofxFaceTracker& tracker) {
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

CellList TransformTableWriter::getHeaders() {
  return {
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
  };
}

CellList TransformTableWriter::buildFrameCells(const ofVideoPlayer& video,
                                               const ofxFaceTracker& tracker) {
  auto frame = video.getCurrentFrame();
  if (!tracker.getFound()) {
    return {
      ofToString(frame),
      "0",

      // position
      "", "",

      // scale
      "",

      // orientation
      "", "", "",

      // direction
      "",

      // rotattion matrix
      "", "", "", "",
      "", "", "", "",
      "", "", "", "",
      "", "", "", "",
    };
  }
  auto pos = tracker.getPosition();
  auto scale = tracker.getScale();
  auto orient = tracker.getOrientation();
  auto dir = tracker.getDirection();
  auto rot = tracker.getRotationMatrix();
  return {
    ofToString(frame),
    "1",

    // position
    ofToString(pos.x), ofToString(pos.y),

    // scale
    ofToString(scale),

    // orientation
    ofToString(orient.x), ofToString(orient.y), ofToString(orient.z),

    // direction
    enumToString(dir),

    // rotation matrix
    ofToString(rot(0, 0)), ofToString(rot(0, 1)), ofToString(rot(0, 2)), ofToString(rot(0, 3)),
    ofToString(rot(1, 0)), ofToString(rot(1, 1)), ofToString(rot(1, 2)), ofToString(rot(1, 3)),
    ofToString(rot(2, 0)), ofToString(rot(2, 1)), ofToString(rot(2, 2)), ofToString(rot(2, 3)),
    ofToString(rot(3, 0)), ofToString(rot(3, 1)), ofToString(rot(3, 2)), ofToString(rot(3, 3)),
  };
}


