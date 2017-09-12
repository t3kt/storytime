#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include "JsonOutput.h"
#include <vector>
#include <memory>

class FrameTableWriter {
public:
  virtual bool setup() = 0;
  virtual void writeFrame(const ofxFaceTracker& tracker) = 0;
  virtual void close();
protected:
  bool initFile(const std::string& path);

  ofFile _file;
};

class MultiFileTableOutput : public TrackingOutput {
public:
  MultiFileTableOutput(const OutputSettings& settings)
  : _settings(settings) {}

  bool setup() override;
  void writeSettings(const Settings& settings) override;
  void writeVideoInfo(const ofVideoPlayer& video) override;
  void writeFrame(const ofxFaceTracker& tracker) override;
  void close() override;

private:
  bool openWritableFile(const std::filesystem::path& path, ofFile* file);

  const OutputSettings& _settings;
  ofDirectory _dir;
  ofFile _settingsFile;
  ofFile _videoInfoFile;
  std::vector<std::shared_ptr<FrameTableWriter>> _frameWriters;
};
