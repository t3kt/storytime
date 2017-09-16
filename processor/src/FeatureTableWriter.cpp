#include "FeatureTableWriter.h"
#include "ofxFaceTracker.h"

using Feature = ofxFaceTracker::Feature;

static std::size_t getFeatureLineSize(Feature feature) {
  switch (feature) {
    case Feature::LEFT_EYE_TOP: return 40 - 36;
    case Feature::RIGHT_EYE_TOP: return 40 - 36;
    case Feature::LEFT_JAW: return 9 - 0;
    case Feature::RIGHT_JAW: return 17 - 8;
    case Feature::JAW: return 17 - 0;
    case Feature::LEFT_EYEBROW: return 22 - 17;
    case Feature::RIGHT_EYEBROW: return 27 - 22;
    case Feature::LEFT_EYE: return 42 - 36;
    case Feature::RIGHT_EYE: return 48 - 42;
    case Feature::OUTER_MOUTH: return 60 - 48;
    case Feature::INNER_MOUTH: return 8;
    case Feature::NOSE_BRIDGE: return 31 - 27;
    case Feature::NOSE_BASE: return 36 - 31;
    case Feature::FACE_OUTLINE: return 27;
    case Feature::ALL_FEATURES: return 66 - 0;
  }
}

static const std::size_t trackerSize = 66;

void FeatureTableWriter::writeHeaderRow() {
  for (auto i = 0; i < trackerSize; i++) {
//    if (_is2D) {
//      table().writeHeaderCellsXY("pt_");
//    }
//    table().writeHeaderCellsXYZ(
  }
  // TODO: write feature header
}
