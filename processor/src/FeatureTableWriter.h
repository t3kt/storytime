#pragma once

#include "FrameTableWriter.h"


class FeatureTableWriter
: public FrameTableWriter {
public:
  FeatureTableWriter(std::filesystem::path filepath, bool is2D)
  : FrameTableWriter(filepath)
  , _is2D(is2D) {}
protected:
  void writeHeaderRow() override;

  void writeFrame(const ofVideoPlayer& video,
                  const ofxFaceTracker& tracker) override;
  bool _is2D;
};


