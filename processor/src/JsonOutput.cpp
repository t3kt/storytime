#include "JsonOutput.h"
#include "ofxTJsonIO.h"

using Direction = ofxFaceTracker::Direction;
using Feature = ofxFaceTracker::Feature;
using Gesture = ofxFaceTracker::Gesture;
using namespace ofxTCommon;

ofJson JsonUtil::toJson(const ofPolyline& polyline) {
  ofJson vertObjs = ofJson::array();

  for (const auto& vert : polyline.getVertices()) {
    vertObjs.push_back(JsonUtil::toJson(vert));
  }

  return {
    {"closed", polyline.isClosed()},
    {"verts", vertObjs},
  };
}

bool JsonTrackingOutput::setup() {
  _file.openFromCWD(_settings.file, ofFile::WriteOnly, false);
  if (!_file.canWrite()) {
    return false;
  }
  _file << "{\n";
  return true;
}

void JsonTrackingOutput::writeSettings(const Settings& settings) {
  _file << "\"settings\": " << settings.toJson().dump(2) << ",\n";
}

void JsonTrackingOutput::writeVideoInfo(const ofVideoPlayer& video) {
  ofJson obj = {
    {"file", video.getMoviePath()},
    {"width", video.getWidth()},
    {"height", video.getHeight()},
    {"frameCount", video.getTotalNumFrames()},
    {"duration", video.getDuration()},
  };
  _file << "\"videoInfo\": " << obj.dump(2) << ",\n";
  _file << "\"frames\": [\n";
}

void JsonTrackingOutput::writeFrame(const ofxFaceTracker& tracker) {
  auto obj = ofJson::object();
  if (!tracker.getFound()) {
    obj["missing"] = true;
    _file << obj << "\n";
  } else {

    if (_settings.haarRectangle && tracker.getHaarFound()) {
      obj["haar"] = JsonUtil::toJson(tracker.getHaarRectangle());
    }

    if (_settings.direction) {
      obj["dir"] = JsonUtil::enumToJson(tracker.getDirection());
    }

    if (_settings.transform) {
      obj["pos"] = JsonUtil::toJson(tracker.getPosition());
      obj["scale"] = tracker.getScale();
      obj["orient"] = JsonUtil::toJson(tracker.getOrientation());
      obj["rot"] = JsonUtil::toJson(tracker.getRotationMatrix());
    }

    if (_settings.features) {
      // TODO
    }

    if (_settings.gestures) {
      auto gesturesObj = ofJson::object();
      for (const auto gesture : getEnumInfo<Gesture>().values()) {
        auto value = tracker.getGesture(gesture);
        gesturesObj[enumToString(gesture)] = value;
      }
      obj["gestures"] = gesturesObj;
    }
    _file << obj << ",\n";
  }
  if (_framesSinceFlush > 30) {
    _file.flush();
    _framesSinceFlush = 0;
  } else {
    _framesSinceFlush++;
  }
//  ofLogVerbose() << "Wrote frame: " << obj.dump();
}

void JsonTrackingOutput::close() {
  _file << "]\n";
  _file << "}";
  _file.close();
}
