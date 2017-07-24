# Storytime Data

## Data Structure

* Database
    *  Teller
        * Story
            * Segment
                * TextLine

### Database

The top-level data storage system that contains a collection of stories
from various channels.

### Teller

A person and/or channel the publishes stories. This generally
corresponds to a YouTube channel.

### Story

A video published by a teller (channel) that contains a single narrative.

### Segment

A portion of a Story specified as a range of time.

### Text Line

A portion of spoken text within a story, specified as a range of time
and a string.

## Story Data Streams

Each story has several kinds of data that align over the time of the
story.

* Video/audio
* Facial tracking points
* Text (subtitles)

## Data Pipelines

Each story comes from a (YouTube/etc) audio/video file paired with a
subtitle file.

### Facial tracking

For facial data, the video is loaded into After Effects. It is then
split into chunks because AE facial tracking is slow when dealing with
long videos. Chunks are generally about 1 minute long. After running the
face tracker, the keyframes are copied from the timeline and pasted into
text files. A separate chunk list file specifies the start and end times
of each chunk in both time codes and frame numbers. The chunk data files
are then processed to produce files in TouchDesigner DAT format (TSV).

