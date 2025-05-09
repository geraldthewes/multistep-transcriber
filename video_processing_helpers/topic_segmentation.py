from treeseg.treeseg import TreeSeg

def segment_topics(entries: list, config: dict, max_segments: int) -> list:
    """
    Process transcript entries and return with topic annotations

    Args:
        entries: List of transcript entries (dicts)
        config: Configuration dictionary

    Returns:
        List of transcript entries with added 'topic' field
    """
    segmenter = TreeSeg(configs=config, entries=entries)
    segments = segmenter.segment_meeting(max_segments)
    return update_transcript_with_topics(entries, segments)


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

