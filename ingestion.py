import os
import sys
import json
import torch
import logging
import argparse

from mst import VideoTranscriber
from treeseg import Embeddings, ollama_embeddings

# Build config
# Configuration
embeddings_config = Embeddings(
    embeddings_func=ollama_embeddings, # openai_embeddings
    headers={}, # forOpenAI
    model="nomic-embed-text",  # or "text-embedding-ada-002" for openai         
    endpoint=os.getenv("OLLAMA_HOST", "")   # "https://api.openai.com/v1/embeddings"
)
config = {
    "MIN_SEGMENT_SIZE": 10,
    "LAMBDA_BALANCE": 0,
    "UTTERANCE_EXPANSION_WIDTH": 3,
    "EMBEDDINGS": embeddings_config,
    "TEXT_KEY": "transcript"
}


def main():
    parser = argparse.ArgumentParser(description="Transcribe a video using a master document.")
    
    # Add arguments
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument('--max-topics', type=int, default=10,
                      help='Maximum number of topics to create, 0 to skip')
    
    # Parse arguments
    args = parser.parse_args()
    
    video_path = args.video_path
    
    if not os.path.exists(video_path):
        print("Error: File(s) not found")
        sys.exit(1)

    print('Setup')
    transcriber = VideoTranscriber(config)
    print(f'Transcribe {video_path}')
    result, nouns_list = transcriber.transcribe_video(video_path)
    if args.max_topics:
        print(f'Break into topics {video_path}')    
        result, headlines, summary = transcriber.topics(video_path, result, args.max_topics)    
    transcriber.format_transcript(video_path, result, nouns_list, headlines, summary)


    
if __name__ == "__main__":
    main()


