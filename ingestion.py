import os
import sys
import json
import torch
import logging
import argparse

from video_transcriber import VideoTranscriber


def main():
    parser = argparse.ArgumentParser(description="Transcribe a video using a master document.")
    
    # Add arguments
    parser.add_argument("video_path", type=str, help="Path to the video file")
    
    # Parse arguments
    args = parser.parse_args()
    
    video_path = args.video_path
    
    if not os.path.exists(video_path):
        print("Error: File(s) not found")
        sys.exit(1)

    print('Setup')
    transcriber = VideoTranscriber()
    print(f'Transcribe {video_path}')
    result = transcriber.transcribe_video(video_path)
    
    # Save output
    #with open("transcription.md", "w") as f:
    #    f.write(result)
    #print("Transcription complete. Output saved to transcription.md")

    
if __name__ == "__main__":
    main()


