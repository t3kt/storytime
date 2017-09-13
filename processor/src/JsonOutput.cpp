#include "JsonOutput.h"
#include "ofxTJsonIO.h"
#include <functional>

using Direction = ofxFaceTracker::Direction;
using Feature = ofxFaceTracker::Feature;
using Gesture = ofxFaceTracker::Gesture;
using namespace ofxTCommon;

using FeatureGetter = std::function<ofPolyline(Feature)>;

ofJson featuresToJson(FeatureGetter getter) {
  ofJson obj = ofJson::object();
  for (auto feature : getEnumInfo<Feature>().values()) {
    auto polyline = getter(feature);
    auto polylineObj = JsonUtil::toJson(polyline);
    if (polylineObj.is_null()) {
      continue;
    }
    obj[enumToString(feature)] = polylineObj;
  }
  return obj;
}

ofJson JsonUtil::toJson(const ofPolyline& polyline) {
  if (polyline.size() == 0) {
    return nullptr;
  }
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

ofJson getVideoInfoJson(const ofVideoPlayer& video) {
  return {
    {"file", video.getMoviePath()},
    {"width", video.getWidth()},
    {"height", video.getHeight()},
    {"frameCount", video.getTotalNumFrames()},
    {"duration", video.getDuration()},
  };
}

void JsonTrackingOutput::writeVideoInfo(const ofVideoPlayer& video) {
  ofJson obj = getVideoInfoJson(video);
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

    if (_settings.transform) {
      obj["pos"] = JsonUtil::toJson(tracker.getPosition());
      obj["scale"] = tracker.getScale();
      obj["orient"] = JsonUtil::toJson(tracker.getOrientation());
      obj["rot"] = JsonUtil::toJson(tracker.getRotationMatrix());
      obj["dir"] = JsonUtil::enumToJson(tracker.getDirection());
    }

    if (_settings.imageFeatures) {
      obj["imgFeatures"] = featuresToJson([&](Feature f) {
        return tracker.getImageFeature(f);
      });
    }

    if (_settings.objectFeatures) {
      obj["objFeatures"] = featuresToJson([&](Feature f) {
        return tracker.getObjectFeature(f);
      });
    }

    if (_settings.meanObjectFeatures) {
      obj["meanObjFeatures"] = featuresToJson([&](Feature f) {
        return tracker.getMeanObjectFeature(f);
      });
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
