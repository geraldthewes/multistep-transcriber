from treeseg  import TreeSeg
from ollama import chat
from typing import List

from .caching import cached_file_object

''' Break the transcript into topics '''

TOPIC_MODEL = "gemma3:27b"
EXTENSION_TOPICS = '.topics'


def _generate_topic_outputs(video_path: str, grouped_topic_texts: List[str], llm_prompt_template: str) -> List[str]:
    """
    Generates an output (e.g., headline, summary) for each topic's concatenated transcript text using an LLM and a given prompt.

    Args:
        video_path (str): Path to the video file (can be used for context or logging).
        grouped_topic_texts (List[str]): A list where each string is the
                                         concatenated transcript for a topic.
        llm_prompt_template (str): The prompt template to use for the LLM. The topic text will be appended to this.

    Returns:
        List[str]: A list of generated outputs, corresponding to each topic.
    """
    outputs = []
    if not grouped_topic_texts:
        return []

    for i, topic_text in enumerate(grouped_topic_texts):
        if not topic_text.strip():
            # Add an empty output for topics with no text content
            outputs.append("")
            print(f"Topic {i} has no text, skipping LLM generation.")
            continue
        
        print(f"Generating LLM output for topic {i}...")
        try:
            # Construct the full prompt using the template and the topic text
            full_prompt = f"{llm_prompt_template}\n\nTranscript section:\n{topic_text}"
            response = chat(
                model=TOPIC_MODEL, # Consider making MODEL a parameter if it needs to vary with the prompt
                messages=[
                    {'role': 'user', 'content': full_prompt}
                ]
            )
            output_text = response.message.content.strip()
            outputs.append(output_text)
            print(f"Generated LLM output for topic {i}: {output_text}")
        except Exception as e:
            print(f"Error generating LLM output for topic {i}: {e}")
            outputs.append(f"Error: Could not generate LLM output for topic {i}")
    
    return outputs

def _create_outputs_from_transcript_topics(video_path: str, updated_transcript_with_topics: List[dict], llm_prompt: str) -> List[str] | None:
    """
    Internal helper to prepare transcript text grouped by topic and generate outputs (e.g., headlines)
    using a specified LLM prompt. This function does not handle caching itself.
    """
    if not updated_transcript_with_topics:
        print("No transcript entries to process for LLM outputs.")
        return None

    # Determine the range of topic numbers
    topic_numbers = sorted(list(set(
        entry['topic'] for entry in updated_transcript_with_topics if 'topic' in entry and entry['topic'] is not None
    )))

    if not topic_numbers:
        print("No topics found in transcript, skipping LLM output generation.")
        grouped_texts_for_llm = []
    else:
        # Topics are 0-indexed. If max topic is N, list size is N+1.
        max_topic_val = topic_numbers[-1]
        grouped_texts_for_llm = [""] * (max_topic_val + 1)
        
        for entry in updated_transcript_with_topics:
            topic_idx = entry.get('topic')
            if topic_idx is not None and 0 <= topic_idx <= max_topic_val:
                # Concatenate transcript texts for the same topic
                if grouped_texts_for_llm[topic_idx]:
                    grouped_texts_for_llm[topic_idx] += " " + entry['transcript']
                else:
                    grouped_texts_for_llm[topic_idx] = entry['transcript']
            elif topic_idx is not None:
                print(f"Warning: Encountered topic index {topic_idx} outside expected range [0, {max_topic_val}] during text preparation.")
    
    if grouped_texts_for_llm:
        return _generate_topic_outputs(video_path, grouped_texts_for_llm, llm_prompt)
    elif not topic_numbers: # Already printed "No topics found..."
        # This case implies no topics, so no texts, and thus no outputs.
        pass
    else: # topic_numbers existed, but somehow grouped_texts_for_llm is empty
        print("No text content found for topics, skipping LLM output generation.")
    return None # Or [] if an empty list is preferred over None for "no output generated"


HEADLINE_PROMPT = "You are a talented local reporter. You have been asked to provide a single descriptive headline to introduce the following section of a transcript from a town meeting for the town audience. Only return the headline with no justification or explanation."


@cached_file_object('.topic_headlines')
def prepare_and_generate_headlines(video_path: str, updated_transcript_with_topics: List[dict]):
    """
    Prepares transcript text grouped by topic and generates headlines using the default prompt.
    The result is cached based on '.topic_headlines'.
    """
    return _create_outputs_from_transcript_topics(video_path, updated_transcript_with_topics, HEADLINE_PROMPT)


SUMMARY_PROMPT = "You are a talented local reporter. You have been asked to provide a one or two sentence max descriptive summary of the the following section of a transcript from a town meeting for the town audience. Just return your proposed summary with no explanation or justification for your choice."

@cached_file_object('.topic_summary')
def prepare_and_generate_summary(video_path: str, updated_transcript_with_topics: List[dict]):
    """
    Prepares transcript text grouped by topic and generates headlines using the default prompt.
    The result is cached based on '.topic_headlines'.
    """
    return _create_outputs_from_transcript_topics(video_path, updated_transcript_with_topics, SUMMARY_PROMPT)


@cached_file_object(EXTENSION_TOPICS)
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

