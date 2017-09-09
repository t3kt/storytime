#include "TrackingProcessor.h"

void TrackingProcessor::setup(const Settings& settings,
                              std::shared_ptr<TrackingOutput> output) {
  _output = output;
  _output->setup(settings);
}

void TrackingProcessor::close() {
  if (_output) {
    _output->close();
    _output = nullptr;
  }
  if (_video.isLoaded()) {
    _video.closeMovie();
  }
}

bool TrackingProcessor::processNextFrame() {
  // TODO
  return false;
}
