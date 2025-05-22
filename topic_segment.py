'''
Break transcript into segments
'''

import os, sys
import json
import argparse

from topic_treeseg import Embeddings, ollama_embeddings

from  video_processing_helpers import segment_topics


def main():
    """CLI for transcript segmentation"""
    parser = argparse.ArgumentParser(description='Break transcript into segments')
    parser.add_argument('transcript', help='Path to input transcript file')
    parser.add_argument('--output', default='segmented_transcript.json',
                      help='Path for output file')
    parser.add_argument('--max-segments', type=int, default=10,
                      help='Maximum number of segments to create')

    args = parser.parse_args()

    # Load and parse transcript
    with open(args.transcript, 'r') as f:
        transcript = json.load(f)

    # Build config
    # Configuration
    embeddings_config = Embeddings(
            embeddings_func=ollama_embeddings, # openai_embeddings
            headers={}, # forOpenAI
            model="nomic-embed-text",  # or "text-embedding-ada-002" for openai         
            endpoint=os.getenv("OLLAMA_HOST", "")   # "https://api.openai.com/v1/embeddings"
    )
    config = {
         "MIN_SEGMENT_SIZE": 5,
         "LAMBDA_BALANCE": 0,
         "UTTERANCE_EXPANSION_WIDTH": 2,
         "EMBEDDINGS": embeddings_config,
         "TEXT_KEY": "transcript"
    }

    # Process transcript
    processed_transcript = segment_topics(transcript, config, args.max_segments)

    # Write output
    with open(args.output, 'w') as f:
        json.dump(processed_transcript, f, indent=2)

if __name__ == "__main__":
    main()



