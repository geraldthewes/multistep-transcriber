from youtube_transcript_api import YouTubeTranscriptApi
import json
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Fetch YouTube transcript by video ID.')
parser.add_argument('video_id', type=str, help='The YouTube video ID')

# Parse arguments
args = parser.parse_args()
video_id = args.video_id

ytt_api = YouTubeTranscriptApi()
fetched_transcript = ytt_api.fetch(video_id)

# Save
output_file = video_id + ".yt_transcript"
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(fetched_transcript.to_raw_data(), file, ensure_ascii=False, indent=4)
