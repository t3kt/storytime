#pragma once

#include "FrameTableWriter.h"
#include <string>
#include <vector>

template<typename P>
std::vector<std::string> pointHeaderSuffixes();

template<>
std::vector<std::string> pointHeaderSuffixes<ofVec2f>() {
  return { "x", "y" };
}

template<>
std::vector<std::string> pointHeaderSuffixes<ofVec3f>() {
  return { "x", "y", "z" };
}

template<typename P>
std::size_t pointPartCount();

template<>
std::size_t pointPartCount<ofVec2f>() { return 2; }
template<>
std::size_t pointPartCount<ofVec3f>() { return 3; }

template<typename P>
class PointsTableWriter
: public FrameTableWriter {
public:
  PointsTableWriter(const ofVideoPlayer& video,
                    const ofxFaceTracker& tracker,
                    std::filesystem::path filepath)
  : FrameTableWriter(video, tracker, filepath) {}
protected:
  void writeHeaderRow() override {
    // TODO...
  }

  void writeFrame() override {
    // TODO...
  }
};


