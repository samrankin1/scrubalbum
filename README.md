# scrub.py v0.2.0
Run this script with an album folder as the working directory to normalize its contents for archival purposes.

By default, it will complete these steps in order:
1. Rename audio files into a standard format: {track no.} - {track title}
2. Extract album art to serve as a folder icon
3. Convert FFmpeg-compatible audio files to FLAC (16bit @ 44.1kHz)
4. Generate a playlist.m3u for the album

### Requirements
* Python 3.6+
* `music-tag`
* Files have valid track number and track title tags
* Reformatting audio:
  * `ffmpeg-python`
  * A local FFmpeg installation

### Configuration
* `TRACK_INFO`
  * Controls whether some basic attributes of tracks will be printed before processing
  * Useful to initially evaluate the quality and consistency of files
  * Default: `True`


* `NORMALIZE_NAMES`
  * Controls whether files will be renamed
  * Default: `True`


* `EXTRACT_ART`
  * Controls whether album art will be extracted
  * Default: `True`
* `OVERWRITE_ART`
  * Controls whether existing art files will be overwritten
  * Default: `False`
* `ART_FILE_NAME`
  * Determines the name portion of the art file
  * Extension determined by format, no conversions applied
  * Default: `folder`


* `CONVERT_AUDIO`
  * Controls whether audio will be reformatted
  * Default: `True`
* `AUDIO_OUTPUT_EXTENSION`
  * Target format for audio files
  * Default: `flac`
* `COMPRESSION_LEVEL`
  * Controls FFmpeg's general output quality
  * Values range from 0 to 12
  * Default: `12` (best)
* `SAMPLE_FORMAT`
  * Controls FFmpeg's output sample format
  * To view available formats, run `ffmpeg -sample_fmts`
  * Default: `s16`
* `SAMPLE_FORMAT_DEPTH`
  * Reflects `SAMPLE_FORMAT` size in bits
  * Must be set correctly to determine which files should be reformatted
  * Default: `16` (from `s16`)
* `SAMPLE_RATE`
  * Controls FFmpeg's output sample rate
  * Default: `44100`
* `DELETE_AFTER_CONVERT`
  * Controls whether the old file will be deleted after reformatting
  * `False` is incompatible with `GENERATE_PLAYLIST`
  * Default: `True`
* `FFMPEG_LOG_LEVEL`
  * Controls the detail of FFmpeg's console output
  * Default: `warning`


* `GENERATE_PLAYLIST`
  * Controls whether a playlist file will be created
  * Default: `True`
* `PLAYLIST_FILE`
  * Full name of the created playlist file
  * Default: `playlist.m3u`
