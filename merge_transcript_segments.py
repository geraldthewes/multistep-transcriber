import argparse
import json
from  video_processing_helpers import merge_transcript_segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge transcript segments into full sentences.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file containing segments.")
    parser.add_argument("output_file", type=str, help="Path to the output JSON file for merged segments.")
    
    args = parser.parse_args()
    
    # Read segments from input file
    with open(args.input_file, 'r') as f:
        segments = json.load(f)
    
    # Merge transcript segments
    merged_segments = merge_transcript_segments(args.input_file, segments)
    
    # Write merged segments to output file
    with open(args.output_file, 'w') as f:
        json.dump(merged_segments, f, indent=4)
