#include "JsonOutput.h"

using Direction = ofxFaceTracker::Direction;
using Feature = ofxFaceTracker::Feature;
using Gesture = ofxFaceTracker::Gesture;

ofJson toJson(const ofVec2f& value) {
  return { value.x, value.y };
}

ofJson toJson(const ofVec3f& value) {
  return { value.x, value.y, value.z };
}

ofJson toJson(const ofVec4f& value) {
  return { value.x, value.y, value.z, value.w };
}

ofJson toJson(const glm::vec2& value) {
  return { value.x, value.y };
}

ofJson toJson(const glm::vec3& value) {
  return { value.x, value.y, value.z };
}

ofJson toJson(const glm::vec4& value) {
  return { value.x, value.y, value.z, value.w };
}

ofJson toJson(const ofMatrix4x4& value) {
  return {
    toJson(value.getRowAsVec4f(0)),
    toJson(value.getRowAsVec4f(1)),
    toJson(value.getRowAsVec4f(2)),
    toJson(value.getRowAsVec4f(3)),
  };
}

ofJson toJson(const ofRectangle& value) {
  return {
    {"x", value.getX() },
    {"y", value.getY() },
    {"w", value.getWidth() },
    {"h", value.getHeight() },
  };
}

ofJson toJson(Direction value) {
  switch (value) {
    case Direction::FACING_FORWARD:
      return "forward";
    case Direction::FACING_LEFT:
      return "left";
    case Direction::FACING_RIGHT:
      return "right";
    case Direction::FACING_UNKNOWN:
    default:
      return nullptr;
  }
}

ofJson toJson(Feature value) {
  switch (value) {
    case Feature::LEFT_EYE_TOP:
      return "leftEyeTop";
    case Feature::RIGHT_EYE_TOP:
      return "rightEyeTop";
    case Feature::LEFT_EYEBROW:
      return "leftEyebrow";
    case Feature::RIGHT_EYEBROW:
      return "rightEyebrow";
    case Feature::LEFT_EYE:
      return "leftEye";
    case Feature::RIGHT_EYE:
      return "rightEye";
    case Feature::LEFT_JAW:
      return "leftJaw";
    case Feature::RIGHT_JAW:
      return "rightJaw";
    case Feature::JAW:
      return "jaw";
    case Feature::OUTER_MOUTH:
      return "outerMouth";
    case Feature::INNER_MOUTH:
      return "innerMouth";
    case Feature::NOSE_BRIDGE:
      return "noseBridge";
    case Feature::NOSE_BASE:
      return "noseBase";
    case Feature::FACE_OUTLINE:
      return "faceOutline";
    case Feature::ALL_FEATURES:
      return "all";
    default:
      return nullptr;
  }
}

ofJson toJson(Gesture value) {
  switch (value) {
    case Gesture::MOUTH_WIDTH:
      return "mouthWidth";
    case Gesture::MOUTH_HEIGHT:
      return "mouthHeight";
    case Gesture::LEFT_EYEBROW_HEIGHT:
      return "leftEyebrowHeight";
    case Gesture::RIGHT_EYEBROW_HEIGHT:
      return "rightEyebrowHeight";
    case Gesture::LEFT_EYE_OPENNESS:
      return "leftEyeOpenness";
    case Gesture::RIGHT_EYE_OPENNESS:
      return "rightEyeOpenness";
    case Gesture::JAW_OPENNESS:
      return "jawOpenness";
    case Gesture::NOSTRIL_FLARE:
      return "nostrilFlare";
    default:
      return nullptr;
  }
}

ofJson toJson(const ofPolyline& polyline) {
  ofJson vertObjs = ofJson::array();

  for (const auto& vert : polyline.getVertices()) {
    vertObjs.push_back(toJson(vert));
  }

  return {
    {"closed", polyline.isClosed()},
    {"verts", vertObjs},
  };
}

bool JsonTrackingOutput::setup() {
  _file = ofFile(_settings.file, ofFile::WriteOnly);
  if (!_file.canWrite()) {
    return false;
  }
  return true;
}

void JsonTrackingOutput::writeVideoInfo(const ofVideoPlayer& video) {
  _infoObj = {
    {"file", video.getMoviePath()},
    {"width", video.getWidth()},
    {"height", video.getHeight()},
    {"frameCount", video.getTotalNumFrames()},
    {"duration", video.getDuration()},
  };
}

void JsonTrackingOutput::writeFrame(const ofxFaceTracker& tracker) {
  ofJson obj = {};
  if (!tracker.getFound()) {
    obj["missing"] = true;
  } else {

    if (_settings.haarRectangle && tracker.getHaarFound()) {
      obj["haar"] = toJson(tracker.getHaarRectangle());
    }

    if (_settings.direction) {
      obj["dir"] = toJson(tracker.getDirection());
    }

    if (_settings.transform) {
      obj["pos"] = toJson(tracker.getPosition());
      obj["scale"] = tracker.getScale();
      obj["orient"] = toJson(tracker.getOrientation());
      obj["rot"] = toJson(tracker.getRotationMatrix());
    }

    if (_settings.features) {
      // TODO
    }

    if (_settings.gestures) {
      // TODO
    }
  }
  _frameObjs.push_back(obj);
}

void JsonTrackingOutput::save() {
  ofJson dataObj = {
    {"frames", _frameObjs},
  };
  try {
    _file << dataObj;
  } catch (std::exception &e) {
    ofLogError("JsonTrackingOutput::save()") << "Error saving json: " << e.what();
  } catch (...) {
    ofLogError("JsonTrackingOutput::save()") << "Error saving json";
  }
}
