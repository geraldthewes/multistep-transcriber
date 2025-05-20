from treeseg.treeseg import TreeSeg
from ollama import chat
from typing import List

from .caching import cached_file_object

''' Break the transcript into topics '''

HEADLINE_MODEL = "gemma3:27b"
HEADLINE_PROMPT = "You are a talented local reporter. You have been asked to provide a single descriptive headline to introduce the following section of a transcript from a town meeting for the town audience. Only return the headline with no justification or explanation."

@cached_file_object('.topic_headlines')
def generate_topic_headlines(video_path: str, grouped_topic_texts: List[str]) -> List[str]:
    """
    Generates a headline for each topic's concatenated transcript text using an LLM.

    Args:
        video_path (str): Path to the video file, used for caching.
        grouped_topic_texts (List[str]): A list where each string is the
                                         concatenated transcript for a topic.
                                         The index corresponds to the topic number.

    Returns:
        List[str]: A list of headlines, corresponding to each topic.
    """
    headlines = []
    if not grouped_topic_texts:
        return []

    for i, topic_text in enumerate(grouped_topic_texts):
        if not topic_text.strip():
            # Add an empty headline for topics with no text content
            headlines.append("")
            print(f"Topic {i} has no text, skipping headline generation.")
            continue
        
        print(f"Generating headline for topic {i}...")
        try:
            full_prompt = f"{HEADLINE_PROMPT}\n\nTranscript section:\n{topic_text}"
            response = chat(
                model=HEADLINE_MODEL,
                messages=[
                    {'role': 'user', 'content': full_prompt}
                ]
            )
            headline = response.message.content.strip()
            headlines.append(headline)
            print(f"Generated headline for topic {i}: {headline}")
        except Exception as e:
            print(f"Error generating headline for topic {i}: {e}")
            headlines.append(f"Error: Could not generate headline for topic {i}")
    
    return headlines


def _prepare_and_generate_headlines(video_path: str, updated_transcript_with_topics: List[dict]):
    """
    Prepares transcript text grouped by topic and generates headlines.
    """
    if not updated_transcript_with_topics:
        print("No transcript entries to process for headlines.")
        return

    # Determine the range of topic numbers
    topic_numbers = sorted(list(set(
        entry['topic'] for entry in updated_transcript_with_topics if 'topic' in entry and entry['topic'] is not None
    )))

    if not topic_numbers:
        print("No topics found in transcript, skipping headline generation.")
        grouped_texts_for_headlines = []
    else:
        # Topics are 0-indexed. If max topic is N, list size is N+1.
        max_topic_val = topic_numbers[-1]
        grouped_texts_for_headlines = [""] * (max_topic_val + 1)
        
        for entry in updated_transcript_with_topics:
            topic_idx = entry.get('topic')
            if topic_idx is not None and 0 <= topic_idx <= max_topic_val:
                # Concatenate transcript texts for the same topic
                if grouped_texts_for_headlines[topic_idx]:
                    grouped_texts_for_headlines[topic_idx] += " " + entry['transcript']
                else:
                    grouped_texts_for_headlines[topic_idx] = entry['transcript']
            elif topic_idx is not None:
                # This should not happen if max_topic_val is derived correctly from existing topics
                print(f"Warning: Encountered topic index {topic_idx} outside expected range [0, {max_topic_val}] during headline text preparation.")
    
    if grouped_texts_for_headlines:
        # This call will generate headlines and cache them via the decorator
        generate_topic_headlines(video_path, grouped_texts_for_headlines)
    elif not topic_numbers: # Already printed "No topics found..."
        pass
    else: # topic_numbers existed, but somehow grouped_texts_for_headlines is empty
        print("No text content found for topics, skipping headline generation.")


@cached_file_object('.topics')
def segment_topics(video_path: str, entries: list, config: dict, max_segments: int) -> list:
    """
    Process transcript entries, assign topic numbers, and generate/cache topic headlines.

    Args:
        video_path (str): Path to the video file.
        entries: List of transcript entries (dicts).
        config: Configuration dictionary for TreeSeg.
        max_segments: Maximum number of segments for topic segmentation.

    Returns:
        List of transcript entries with added 'topic' field.
    """
    segmenter = TreeSeg(configs=config, entries=entries)
    segments = segmenter.segment_meeting(max_segments)
    updated_transcript_with_topics = update_transcript_with_topics(entries, segments)

    # Generate and cache topic headlines
    _prepare_and_generate_headlines(video_path, updated_transcript_with_topics)

    return updated_transcript_with_topics


def update_transcript_with_topics(transcript, topic_transitions):
    """
    Updates transcript entries with topic numbers based on topic transitions.
    
    Args:
        transcript: List of transcript entry dictionaries
        topic_transitions: List of 0s and 1s indicating topic continuation (0) or new topic (1)
    
    Returns:
        Updated transcript with topic field added to each entry
    """
    if len(transcript) != len(topic_transitions):
        raise ValueError("Length of transcript and topic_transitions must match")
    
    current_topic = 0
    for i, (entry, transition) in enumerate(zip(transcript, topic_transitions)):
        if transition == 1:
            current_topic += 1
        entry['topic'] = current_topic
    
    return transcript

