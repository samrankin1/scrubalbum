import os
import time
from functools import cmp_to_key

VERSION = '0.1.0'

# script config start

AUDIO_EXTENSIONS = ['aac', 'aiff', 'dsf', 'flac', 'm4a', 'mp3', 'ogg', 'opus', 'wav', 'wv']

TRACK_INFO = True

NORMALIZE_NAMES = True

EXTRACT_ART = True
OVERWRITE_ART = False
ART_FILE_NAME = 'folder'

CONVERT_AUDIO = True
AUDIO_OUTPUT_EXTENSION = 'flac'
DELETE_AFTER_CONVERT = True  # False is incompatible with GENERATE_PLAYLIST
FFMPEG_LOG_LEVEL = 'warning'  # 'info' for more output, 'quiet' for none

GENERATE_PLAYLIST = True
PLAYLIST_FILE = 'playlist.m3u'

# script config end

if NORMALIZE_NAMES:
	import re
	ILLEGAL_CHARS = re.compile(r"[<>:\"/\\|?*]")  # <>:"/\|?*

if NORMALIZE_NAMES or EXTRACT_ART:
	import music_tag

if CONVERT_AUDIO:
	import ffmpeg


def _scan_files(path='.'):
	parts = [f.name.rpartition('.') for f in os.scandir(path) if f.is_file()]
	return [(name, ext) for name, _, ext in parts]


def _cmp_track_number(a, b):
	a_num = int(a.raw['tracknumber'].value)
	b_num = int(b.raw['tracknumber'].value)
	return a_num - b_num


def track_info():
	tracks = [music_tag.load_file(name + '.' + ext) for name, ext in _scan_files() if ext in AUDIO_EXTENSIONS]
	tracks = sorted(tracks, key=cmp_to_key(_cmp_track_number))

	for track in tracks:

		codec = track['#codec'].value
		length_s = track['#length'].value
		channels = track['#channels'].value
		bits_ps = track['#bitspersample'].value
		sample_rate = track['#samplerate'].value
		bit_rate = track['#bitrate'].value
		print(
			"track_info: '{}' [{} {:d}:{:04.1f}] {:d}ch {:d}bit@{:0.1f}kHz {:0.1f}kbps"
			.format(
				track.filename, codec,
				int(length_s / 60), length_s % 60,
				channels, bits_ps, sample_rate / 1000, bit_rate / 1000
			)
		)


def normalize_names():
	files = _scan_files()

	for name, ext in files:
		if ext not in AUDIO_EXTENSIONS:
			continue

		dirty_name = name + '.' + ext
		tags = music_tag.load_file(dirty_name)

		# handles files with unrecognized totaltracks data (e.g tracknumber = '1/10')
		raw_track_num = tags.raw['tracknumber'].value
		track_num = str(int(raw_track_num.split('/')[0]))

		# replaces characters unsuitable for file names with _
		track_title = ILLEGAL_CHARS.sub('_', tags['tracktitle'].value)

		normal_name = track_num + ' - ' + track_title + '.' + ext

		if dirty_name != normal_name:
			os.rename(dirty_name, normal_name)
			print("normalize_names: '" + dirty_name + "' => '" + normal_name + "'")


def extract_art():
	files = _scan_files()

	if not OVERWRITE_ART:
		for name, _ in files:
			if name == ART_FILE_NAME:
				return

	for name, ext in files:
		if ext not in AUDIO_EXTENSIONS:
			continue

		audio_file = name + '.' + ext
		tags = music_tag.load_file(audio_file)

		try:
			art = tags['artwork'].value
			art_ext = art.format
			art_raw = art.raw
		except (KeyError, ValueError):
			continue

		art_file = ART_FILE_NAME + '.' + art_ext
		with open(art_file, 'wb') as file:
			file.write(art_raw)

		print("extract_art: extracted '" + art_file + "' from '" + audio_file + "'")
		return

	print('[ERR] extract_art: could not find artwork to extract')


def convert_audio():
	files = _scan_files()

	for name, ext in files:
		if ext not in AUDIO_EXTENSIONS or ext == AUDIO_OUTPUT_EXTENSION:
			continue

		old_file = name + '.' + ext
		new_file = name + '.' + AUDIO_OUTPUT_EXTENSION
		(
			ffmpeg
			.input(old_file)
			.output(new_file, compression_level=12, vsync=0, loglevel=FFMPEG_LOG_LEVEL)
			.run()
		)

		if DELETE_AFTER_CONVERT:
			os.remove(old_file)

		print("convert_audio: '" + old_file + "' => '" + new_file + "'")


def generate_playlist():
	files = _scan_files()
	playlist = list()

	i = 1
	while True:
		matches = [name + '.' + ext for name, ext in files if name.startswith(str(i) + ' ') and ext in AUDIO_EXTENSIONS]
		matches_n = len(matches)

		if matches_n > 1:
			print('[ERR] generate_playlist: expected 1 file for track #' + str(i) + ', got ' + str(matches_n) + 'files')
			break

		elif matches_n == 1:
			playlist.append(matches[0])

		else:  # matches_n == 0
			with open(PLAYLIST_FILE, 'w') as file:

				for song in playlist:
					file.write(song + '\n')

			print('generate_playlist: wrote out ' + str(i-1) + ' tracks')
			break

		i += 1


start_time = time.perf_counter()
print('--- start scrub v' + VERSION + ' ---')

if TRACK_INFO:
	track_info()

if NORMALIZE_NAMES:
	normalize_names()

if EXTRACT_ART:
	extract_art()

if CONVERT_AUDIO:
	convert_audio()

if GENERATE_PLAYLIST:
	generate_playlist()

print(
	'--- end scrub ({:05.3f}s) ---'
	.format(time.perf_counter() - start_time)
)
