#include "TrackingProcessor.h"

bool TrackingProcessor::setup(Settings settings) {
  _settings = settings;
  ofLogNotice() << "TrackingProcessor::setup() settings: " << _settings;
  _output = TrackingOutput::createOutput(_video, _tracker, _settings.output);
  if (!_output) {
    return false;
  }
  if (!_output->setup()) {
    return false;
  }
  _output->writeSettings(_settings);
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
  _output->writeVideoInfo();
  return true;
}

void TrackingProcessor::close() {
  ofLogNotice() << "BEGIN TrackingProcessor::close()";
  if (_output) {
    _output->close();
    _output = nullptr;
  }
  if (_video.isLoaded()) {
    _video.closeMovie();
  }
  ofLogNotice() << "END TrackingProcessor::close()";
}

bool TrackingProcessor::processNextFrame() {
  _video.update();
  if (!_tracker.getFound()) {
    _deadFrames++;
    if (_deadFrames > 30) {
      ofLogWarning() << "Too many dead frames! Stopping!!";
      return false;
    }
  } else {
    _deadFrames = 0;
  }
  if (!_video.isFrameNew()) {
    return true;
  }
  ofLogNotice() << "TrackingProcessor - processing frame: " << _video.getCurrentFrame() << " / " << _video.getTotalNumFrames();
  if (_video.getIsMovieDone()) {
    ofLogNotice() << "TrackingProcessor - movie is done!";
    return false;
  }
  _video.nextFrame();
  _tracker.update(ofxCv::toCv(_video));
  _output->writeFrame();
  return true;
}
