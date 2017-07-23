# Storytime Data

## Data Structure

* Database
    *  Channel
        * Story
            * Segment

### Database

The top-level data storage system that contains a collection of stories
from various channels.

### Channel

A person and/or channel the publishes stories. This generally
corresponds to a YouTube channel.

### Story

A video published by a channel that contains a single narrative.

### Segment

A portion of a Story specified as a range of time.

## Story Data Streams

Each story has several kinds of data that align over the time of the
story.

* Video/audio
* Facial tracking points
* Text (subtitles)
