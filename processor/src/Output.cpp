#include "Output.h"
#include "JsonOutput.h"
#include "MultiFileTableOutput.h"
#include "ofxTEnums.h"
#include <ofMain.h>

std::shared_ptr<TrackingOutput>
TrackingOutput::createOutput(const OutputSettings& settings) {
  switch (settings.format) {
    case OutputFormat::JSON:
      return std::make_shared<JsonTrackingOutput>(settings);
    case OutputFormat::MULTIFILE:
      return std::make_shared<MultiFileTableOutput>(settings);
    default:
      ofLogError("TrackingOutput::createOutput()") << "unsupported format: " << ofxTCommon::enumToString(settings.format);
      return nullptr;
  }
}
