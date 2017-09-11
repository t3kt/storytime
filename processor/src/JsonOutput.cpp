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
      obj["haar"] = JsonUtil::toJson(tracker.getHaarRectangle());
    }

    if (_settings.direction) {
      obj["dir"] = JsonUtil::toJson(tracker.getDirection());
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
      // TODO
    }
  }
//  ofLogVerbose() << "Wrote frame: " << obj.dump();
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
