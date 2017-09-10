#include "Settings.h"

std::string formatToString(OutputFormat value) {
  switch (value) {
    case OutputFormat::JSON:
      return "json";
    default:
      return "unknown";
  }
}

OutputFormat stringToFormat(const std::string& value) {
  if (value == "json") {
    return OutputFormat::JSON;
  }
  return OutputFormat::UNKNOWN;
}

std::ostream& operator<<(std::ostream& os,
                         const OutputFormat& value) {
  return os << formatToString(value);
}

std::string SettingsBase::toString() const {
  return this->toJson().dump();
}

std::ostream& operator<<(std::ostream& os,
                         const SettingsBase& value) {
  return os << value.toString();
}

ofJson OutputSettings::toJson() const {
  return {
    {"format", formatToString(format)},
    {"file", file},
    {"points", points},
    {"meshes", meshes},
    {"haarRectangle", haarRectangle},
    {"transform", transform},
    {"direction", direction},
    {"features", features},
    {"gestures", gestures},
  };
}

void OutputSettings::readJson(const ofJson& obj) {
  
}
