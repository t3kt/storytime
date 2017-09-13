#include "Settings.h"
#include "ofxTEnums.h"

using namespace ofxTCommon;

EnumTypeInfo<OutputFormat> OutputFormatInfo {
  {"unknown", OutputFormat::UNKNOWN},
  {"json", OutputFormat::JSON},
  {"multifile", OutputFormat::MULTIFILE},
};

template<>
const EnumTypeInfo<OutputFormat>& ofxTCommon::getEnumInfo() {
  return OutputFormatInfo;
}

std::ostream& operator<<(std::ostream& os,
                         const OutputFormat& value) {
  os << enumToString(value);
}

std::ostream& operator<<(std::ostream& os,
                         const SettingsBase& value) {
  return os << value.toJsonString();
}

ofJson OutputSettings::toJson() const {
  return {
    {"format", JsonUtil::enumToJson(format)},
    {"file", file},
    {"points", points},
    {"meshes", meshes},
    {"haarRectangle", haarRectangle},
    {"transform", transform},
    {"imageFeatures", imageFeatures},
    {"objectFeatures", objectFeatures},
    {"meanObjectFeatures", meanObjectFeatures},
    {"gestures", gestures},
  };
}

void OutputSettings::readJson(const ofJson& obj) {
  JsonUtil::assertIsObject(obj);
  format = JsonUtil::enumFromJson<OutputFormat>(obj["format"]);
  file = JsonUtil::fromJsonField(obj, "file", file);
  points = JsonUtil::fromJsonField(obj, "points", false);
  meshes = JsonUtil::fromJsonField(obj, "meshes", false);
  haarRectangle = JsonUtil::fromJsonField(obj, "haarRectangle", false);
  transform = JsonUtil::fromJsonField(obj, "transform", false);
  imageFeatures = JsonUtil::fromJsonField(obj, "imageFeatures", false);
  objectFeatures = JsonUtil::fromJsonField(obj, "objectFeatures", false);
  meanObjectFeatures = JsonUtil::fromJsonField(obj, "meanObjectFeatures", false);
  gestures = JsonUtil::fromJsonField(obj, "gestures", false);
}

ofJson TrackerSettings::toJson() const {
  return {
    {"rescale", rescale},
    {"iterations", iterations},
    {"clamp", clamp},
    {"tolerance", tolerance},
    {"attempts", attempts},
    {"useInvisible", useInvisible},
    {"haarMinSize", haarMinSize},
  };
}

void TrackerSettings::readJson(const ofJson &obj) {
  JsonUtil::assertIsObject(obj);
  rescale = JsonUtil::fromJsonField(obj, "rescale", rescale);
  iterations = JsonUtil::fromJsonField(obj, "iterations", iterations);
  clamp = JsonUtil::fromJsonField(obj, "clamp", clamp);
  tolerance = JsonUtil::fromJsonField(obj, "tolerance", tolerance);
  attempts = JsonUtil::fromJsonField(obj, "attempts", attempts);
  useInvisible = JsonUtil::fromJsonField(obj, "useInvisible", useInvisible);
  haarMinSize = JsonUtil::fromJsonField(obj, "haarMinSize", haarMinSize);
}

ofJson Settings::toJson() const {
  return {
    {"output", output.toJson()},
    {"tracker", tracker.toJson()},
  };
}

void Settings::readJson(const ofJson& obj) {
  JsonUtil::assertIsObject(obj);
  output.readJson(obj["output"]);
  if (!obj["tracker"].is_null()) {
    tracker.readJson(obj["tracker"]);
  }
}
