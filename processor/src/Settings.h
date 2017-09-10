#pragma once

#include <string>
#include <iostream>
#include <ofJson.h>

enum class OutputFormat {
  UNKNOWN,
  JSON,
};

OutputFormat stringToFormat(const std::string& value);

std::string formatToString(OutputFormat value);

std::ostream& operator<<(std::ostream& os,
                         const OutputFormat& value);

class SettingsBase {
public:
  virtual ofJson toJson() const = 0;
  virtual void readJson(const ofJson& obj) = 0;

  std::string toString() const;
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
  bool points;
  bool meshes;
  bool haarRectangle;
  bool transform;
  bool direction;
  bool features;
  bool gestures;
};

class TrackerSettings {
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

  float rescale;
  int iterations;
  float clamp;
  float tolerance;
  int attempts;
  bool useInvisible;
  float haarMinSize;
};

class Settings {
public:
  OutputSettings output;
  TrackerSettings tracker;
};
