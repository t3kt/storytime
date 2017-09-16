#pragma once

#include "ofMain.h"
#include "ofxFaceTracker.h"
#include "Output.h"
#include "Settings.h"

class MultiFileTableOutput : public TrackingOutput {
public:
  MultiFileTableOutput(const ofVideoPlayer& video,
                       const ofxFaceTracker& tracker,
                       const OutputSettings& settings)
  : TrackingOutput(video, tracker)
  , _settings(settings) {}

  bool setup() override;
  void writeSettings(const Settings& settings) override;
  void writeVideoInfo() override;
  void writeFrame() override;
  void close() override;

private:
  std::filesystem::path getFilePath(const std::filesystem::path& path) const;
  bool openWritableFile(const std::filesystem::path& path, ofFile* file);
  bool addFrameWriter(std::shared_ptr<FrameWriter> writer);

  const OutputSettings& _settings;
  ofDirectory _dir;
  ofFile _settingsFile;
  ofFile _videoInfoFile;
  std::vector<std::shared_ptr<FrameWriter>> _frameWriters;
};
