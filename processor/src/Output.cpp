#include "Output.h"
#include "JsonOutput.h"
#include <ofMain.h>

std::shared_ptr<TrackingOuput>
TrackingOuput::createOutput(const OutputSettings& settings) {
  switch (settings.format) {
    case OutputFormat::JSON:
      return std::make_shared<JsonTrackingOutput>(settings);
    default:
      ofLogError("TrackingOutput::createOutput()") << "unsupported format: " << formatToString(settings.format);
      return nullptr;
  }
}
