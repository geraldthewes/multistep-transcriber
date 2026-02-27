"""
Centralized configuration for the multistep-transcriber package.

All model names, thresholds, and environment-driven settings are defined here.
Use TranscriberConfig.from_env() to construct a config that reads the same
environment variables as the previous per-module defaults.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for the LLM client."""

    provider: str = "openai"
    openai_base_url: str = "http://glm-flash.cluster:9999/v1"
    openai_api_key: str = "not-needed"


class TranscriptionConfig(BaseModel):
    """Configuration for the Whisper transcription step."""

    whisper_model: str = "distil-large-v3"


class MergeSentencesConfig(BaseModel):
    """Configuration for the sentence-merging step."""

    spacy_model: str = "en_core_web_sm"


class EntityConfig(BaseModel):
    """Configuration for the entity-extraction step."""

    gliner_model: str = "urchade/gliner_medium-v2.1"
    entity_threshold: float = 0.65
    similar_names_model: str = "glm-4.7-flash"


class StandardizeConfig(BaseModel):
    """Configuration for the transcript-standardization step."""

    sentence_transformer_model: str = "paraphrase-MiniLM-L6-v2"
    similarity_threshold: float = 0.85


class DiarizationConfig(BaseModel):
    """Configuration for the speaker-diarization step."""

    diarization_model: str = "pyannote/speaker-diarization-3.1"
    hf_token: Optional[str] = None


class IntroductionsConfig(BaseModel):
    """Configuration for the speaker-introduction detection and mapping steps."""

    setfit_model: str = "gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction"
    speaker_map_margin: float = 1.0
    entity_map_margin: float = 0.5


class TopicConfig(BaseModel):
    """Configuration for the topic-segmentation step."""

    topic_model: str = "glm-4.7-flash"
    headline_prompt: str = (
        "You are a talented local reporter. You have been asked to provide a single"
        " descriptive headline to introduce the following section of a transcript from"
        " a town meeting for the town audience. Only return the headline with no"
        " justification or explanation."
    )
    summary_prompt: str = (
        "You are a talented local reporter. You have been asked to provide a one or"
        " two sentence max descriptive summary of the the following section of a"
        " transcript from a town meeting for the town audience. Just return your"
        " proposed summary with no explanation or justification for your choice."
    )


class TranscriberConfig(BaseModel):
    """Top-level configuration for the VideoTranscriber pipeline."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    merge_sentences: MergeSentencesConfig = Field(default_factory=MergeSentencesConfig)
    entities: EntityConfig = Field(default_factory=EntityConfig)
    standardize: StandardizeConfig = Field(default_factory=StandardizeConfig)
    diarization: DiarizationConfig = Field(default_factory=DiarizationConfig)
    introductions: IntroductionsConfig = Field(default_factory=IntroductionsConfig)
    topic: TopicConfig = Field(default_factory=TopicConfig)

    @classmethod
    def from_env(cls) -> "TranscriberConfig":
        """
        Build a TranscriberConfig by reading the environment variables that were
        previously consumed at module level in the individual step files.

        Environment variables read:
          - LLM_PROVIDER       (default: "openai")
          - OPENAI_BASE_URL    (default: "http://glm-flash.cluster:9999/v1")
          - OPENAI_API_KEY     (default: "not-needed")
          - HF_TOKEN           (default: None)
          - SIMILAR_NAMES_MODEL (default: "glm-4.7-flash")
          - TOPIC_MODEL        (default: "glm-4.7-flash")
        """
        llm = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            openai_base_url=os.getenv(
                "OPENAI_BASE_URL", "http://glm-flash.cluster:9999/v1"
            ),
            openai_api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
        )
        diarization = DiarizationConfig(
            hf_token=os.environ.get("HF_TOKEN"),
        )
        entities = EntityConfig(
            similar_names_model=os.getenv("SIMILAR_NAMES_MODEL", "glm-4.7-flash"),
        )
        topic = TopicConfig(
            topic_model=os.getenv("TOPIC_MODEL", "glm-4.7-flash"),
        )
        return cls(
            llm=llm,
            diarization=diarization,
            entities=entities,
            topic=topic,
        )
