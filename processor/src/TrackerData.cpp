#include "TrackerData.h"

using namespace ofxTCommon;

EnumTypeInfo<Direction> DirectionInfo {
  {"forward", Direction::FACING_FORWARD},
  {"left", Direction::FACING_LEFT},
  {"right", Direction::FACING_RIGHT},
};

template<>
const EnumTypeInfo<Direction>& ofxTCommon::getEnumInfo() {
  return DirectionInfo;
}

EnumTypeInfo<Feature> FeatureInfo {
  {"leftEyeTop", Feature::LEFT_EYE_TOP},
  {"rightEyeTop", Feature::RIGHT_EYE_TOP},
  {"leftEyebrow", Feature::LEFT_EYEBROW},
  {"rightEyebrow", Feature::RIGHT_EYEBROW},
  {"leftEye", Feature::LEFT_EYE},
  {"rightEye", Feature::RIGHT_EYE},
  {"leftJaw", Feature::LEFT_JAW},
  {"rightJaw", Feature::RIGHT_JAW},
  {"jaw", Feature::JAW},
  {"outerMouth", Feature::OUTER_MOUTH},
  {"innerMouth", Feature::INNER_MOUTH},
  {"noseBridge", Feature::NOSE_BRIDGE},
  {"noseBase", Feature::NOSE_BASE},
  {"faceOutline", Feature::FACE_OUTLINE},
  {"all", Feature::ALL_FEATURES},
};

template<>
const EnumTypeInfo<Feature>& ofxTCommon::getEnumInfo() {
  return FeatureInfo;
}

EnumTypeInfo<Gesture> GestureInfo {
  {"mouthWidth", Gesture::MOUTH_WIDTH},
  {"mouthHeight", Gesture::MOUTH_HEIGHT},
  {"leftEyebrowHeight", Gesture::LEFT_EYEBROW_HEIGHT},
  {"rightEyebrowHeight", Gesture::RIGHT_EYEBROW_HEIGHT},
  {"leftEyeOpenness", Gesture::LEFT_EYE_OPENNESS},
  {"rightEyeOpenness", Gesture::RIGHT_EYE_OPENNESS},
  {"jawOpenness", Gesture::JAW_OPENNESS},
  {"nostrilFlare", Gesture::NOSTRIL_FLARE},
};

template<>
const EnumTypeInfo<Gesture>& ofxTCommon::getEnumInfo() {
  return GestureInfo;
}
