#pragma once

#include <string>
#include <iostream>
#include <ofJson.h>
#include "ofxTJsonIO.h"

enum class OutputFormat {
  UNKNOWN,
  JSON,
  MULTIFILE,
};

std::ostream& operator<<(std::ostream& os,
                         const OutputFormat& value);

class SettingsBase
: public ofxTCommon::JsonReadable
, public ofxTCommon::JsonWritable {
public:
};

std::ostream& operator<<(std::ostream& os,
                         const SettingsBase& value);

class OutputSettings : public SettingsBase {
public:
  OutputSettings()
  : format(OutputFormat::JSON) {}

  ofJson toJson() const override;
  void readJson(const ofJson& obj) override;

  OutputFormat format;
  std::string file;
  bool imagePoints;
  bool objectPoints;
  bool meanObjectPoints;
  bool meshes;
  bool haarRectangle;
  bool transform;
  bool featureIndices;
  bool imageFeatures;
  bool objectFeatures;
  bool meanObjectFeatures;
  bool gestures;
};

class TrackerSettings : public SettingsBase {
public:
  TrackerSettings()
  : rescale(1)
  , iterations(10) // [1-25] 1 is fast and inaccurate, 25 is slow and accurate
  , clamp(3) // [0-4] 1 gives a very loose fit, 4 gives a very tight fit
  , tolerance(.01) // [.01-1] match tolerance
  , attempts(1) // [1-4] 1 is fast and may not find faces, 4 is slow but will find faces
  , useInvisible(true)
  , haarMinSize(30)
  { }

  ofJson toJson() const override;
  void readJson(const ofJson& obj) override;

  float rescale;
  int iterations;
  float clamp;
  float tolerance;
  int attempts;
  bool useInvisible;
  float haarMinSize;
};

class Settings : public SettingsBase {
public:

  ofJson toJson() const override;
  void readJson(const ofJson& obj) override;

  OutputSettings output;
  TrackerSettings tracker;
};
