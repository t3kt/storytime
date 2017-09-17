#pragma once

#include "FrameTableWriter.h"


class FeatureTableWriter
: public FrameTableWriter {
public:
  FeatureTableWriter(const ofVideoPlayer& video,
                     const ofxFaceTracker& tracker,
                     std::filesystem::path filepath,
                     bool is2D)
  : FrameTableWriter(video, tracker, filepath)
  , _is2D(is2D) {}
protected:
  void writeHeaderRow() override;

  void writeFrame() override;
  bool _is2D;
};


