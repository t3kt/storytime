#include "TrackingProcessor.h"

bool TrackingProcessor::setup() {
  _output = TrackingOutput::createOutput(_settings.output);
  if (!_output) {
    return false;
  }
  if (!_output->setup()) {
    return false;
  }
  _tracker.setup();
  _tracker.setRescale(_settings.tracker.rescale);
  _tracker.setIterations(_settings.tracker.iterations);
  _tracker.setClamp(_settings.tracker.clamp);
  _tracker.setTolerance(_settings.tracker.tolerance);
  _tracker.setAttempts(_settings.tracker.attempts);
  _tracker.setUseInvisible(_settings.tracker.useInvisible);
  _tracker.setHaarMinSize(_settings.tracker.haarMinSize);
  return true;
}

bool TrackingProcessor::loadMovie(const std::string& path) {
  if (!_video.load(path)) {
    return false;
  }
  _output->writeVideoInfo(_video);
  return true;
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
  if (_video.getIsMovieDone()) {
    return false;
  }
  _video.nextFrame();
  _tracker.update(ofxCv::toCv(_video));
  _output->writeFrame(_tracker);
  return true;
}
