# scrub.py
Run this script with an album folder as the working directory to normalize its contents for archival purposes.

By default, it will complete these steps in order:
1. Rename audio files into a standard format: {track no.} - {track title}
2. Extract album art to serve as a folder icon
3. Convert FFmpeg-compatible audio files to FLAC without loss of fidelity
4. Generate a playlist.m3u for the album

### Requirements
* Python 3.x
* Normalizing names:
  * `music-tag~=0.4.3`
  * Files have valid track number and track title tags
* Extracting art:
  * `music-tag~=0.4.3`
* Transcoding audio:
  * `ffmpeg-python~=0.2.0`
  * A local FFmpeg installation

### Configuration
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
  * Controls whether audio will be transcoded
  * Default: `True`
* `AUDIO_OUTPUT_EXTENSION`
  * Target format for audio files
  * Files that already have this extension will remain untouched
  * Default: `flac`
* `DELETE_AFTER_CONVERT`
  * Controls whether the old file will be deleted after transcoding
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
