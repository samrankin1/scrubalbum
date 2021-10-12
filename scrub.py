import os
import time
from functools import cmp_to_key

VERSION = '0.1.3'

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


# orders a list of music_tag objects by track number (ascending)
def _cmp_track_number(a, b):
	a_num = int(a.raw['tracknumber'].value.split('/')[0])
	b_num = int(b.raw['tracknumber'].value.split('/')[0])
	return a_num - b_num


def _scan_tracks(path='.'):
	tracks = [music_tag.load_file(f'{name}.{ext}') for name, ext in _scan_files(path) if ext in AUDIO_EXTENSIONS]
	return sorted(tracks, key=cmp_to_key(_cmp_track_number))


def track_info():
	for track in _scan_tracks():

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
	for track in _scan_tracks():

		dirty_name = track.filename

		# handles files with unrecognized totaltracks data (e.g tracknumber = '1/10')
		raw_track_num = track.raw['tracknumber'].value
		track_num = int(raw_track_num.split('/')[0])

		# replaces characters unsuitable for file names with _
		track_title = ILLEGAL_CHARS.sub('_', track['tracktitle'].value)

		# parses the file's extension from its name
		track_ext = dirty_name.rpartition('.')[2]

		normal_name = f'{track_num:d} - {track_title}.{track_ext}'

		if dirty_name != normal_name:
			os.rename(dirty_name, normal_name)
			print(f"normalize_names: '{dirty_name}' => '{normal_name}'")


def extract_art():
	files = _scan_files()

	if not OVERWRITE_ART:
		for name, _ in files:
			if name == ART_FILE_NAME:
				return

	for name, ext in files:
		if ext not in AUDIO_EXTENSIONS:
			continue

		audio_file = f'{name}.{ext}'
		tags = music_tag.load_file(audio_file)

		try:
			art = tags['artwork'].value
			art_ext = art.format
			art_raw = art.raw
		except (KeyError, ValueError):
			continue

		art_file = f'{ART_FILE_NAME}.{art_ext}'
		with open(art_file, 'wb') as file:
			file.write(art_raw)

		print(f"extract_art: extracted '{art_file}' from '{audio_file}'")
		return

	print('[ERR] extract_art: could not find artwork to extract')


def convert_audio():
	files = _scan_files()

	for name, ext in files:
		if ext not in AUDIO_EXTENSIONS or ext == AUDIO_OUTPUT_EXTENSION:
			continue

		old_file = f'{name}.{ext}'
		new_file = f'{name}.{AUDIO_OUTPUT_EXTENSION}'
		(
			ffmpeg
			.input(old_file)
			.output(new_file, compression_level=12, vsync=0, loglevel=FFMPEG_LOG_LEVEL)
			.run()
		)

		if DELETE_AFTER_CONVERT:
			os.remove(old_file)

		print(f"convert_audio: '{old_file}' => '{new_file}'")


def generate_playlist():
	playlist = [f'{track.filename}\n' for track in _scan_tracks()]

	with open(PLAYLIST_FILE, 'w') as file:
		file.writelines(playlist)

	print(f'generate_playlist: wrote out {len(playlist):d} tracks')


start_time = time.perf_counter()
print(f'--- start scrub v{VERSION} ---')

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

print(f'--- end scrub ({(time.perf_counter() - start_time):05.3f}s) ---')
