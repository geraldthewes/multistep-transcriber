"""
Unit tests for the centralized TranscriberConfig and sub-configs.
"""

import os
import unittest

from ...config import (
    DiarizationConfig,
    EntityConfig,
    IntroductionsConfig,
    LLMConfig,
    MergeSentencesConfig,
    StandardizeConfig,
    TopicConfig,
    TranscriptionConfig,
    TranscriberConfig,
)


class TestLLMConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = LLMConfig()
        self.assertEqual(cfg.provider, "openai")
        self.assertEqual(cfg.openai_base_url, "http://glm-flash.cluster:9999/v1")
        self.assertEqual(cfg.openai_api_key, "not-needed")

    def test_custom_values(self):
        cfg = LLMConfig(provider="ollama", openai_base_url="http://localhost:11434", openai_api_key="key")
        self.assertEqual(cfg.provider, "ollama")


class TestTranscriptionConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = TranscriptionConfig()
        self.assertEqual(cfg.whisper_model, "distil-large-v3")


class TestMergeSentencesConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = MergeSentencesConfig()
        self.assertEqual(cfg.spacy_model, "en_core_web_sm")


class TestEntityConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = EntityConfig()
        self.assertEqual(cfg.gliner_model, "urchade/gliner_medium-v2.1")
        self.assertAlmostEqual(cfg.entity_threshold, 0.65)
        self.assertEqual(cfg.similar_names_model, "glm-4.7-flash")


class TestStandardizeConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = StandardizeConfig()
        self.assertEqual(cfg.sentence_transformer_model, "paraphrase-MiniLM-L6-v2")
        self.assertAlmostEqual(cfg.similarity_threshold, 0.85)


class TestDiarizationConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = DiarizationConfig()
        self.assertEqual(cfg.diarization_model, "pyannote/speaker-diarization-3.1")
        self.assertIsNone(cfg.hf_token)

    def test_hf_token(self):
        cfg = DiarizationConfig(hf_token="my-token")
        self.assertEqual(cfg.hf_token, "my-token")


class TestIntroductionsConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = IntroductionsConfig()
        self.assertEqual(cfg.setfit_model, "gerald29/setfit-bge-small-v1.5-sst2-8-shot-introduction")
        self.assertAlmostEqual(cfg.speaker_map_margin, 1.0)
        self.assertAlmostEqual(cfg.entity_map_margin, 0.5)


class TestTopicConfig(unittest.TestCase):

    def test_defaults(self):
        cfg = TopicConfig()
        self.assertEqual(cfg.topic_model, "glm-4.7-flash")
        self.assertIn("headline", cfg.headline_prompt.lower())
        self.assertIn("summary", cfg.summary_prompt.lower())


class TestTranscriberConfig(unittest.TestCase):

    def test_no_args_construction(self):
        """TranscriberConfig() with no args should use all defaults."""
        cfg = TranscriberConfig()
        self.assertIsInstance(cfg.llm, LLMConfig)
        self.assertIsInstance(cfg.transcription, TranscriptionConfig)
        self.assertIsInstance(cfg.merge_sentences, MergeSentencesConfig)
        self.assertIsInstance(cfg.entities, EntityConfig)
        self.assertIsInstance(cfg.standardize, StandardizeConfig)
        self.assertIsInstance(cfg.diarization, DiarizationConfig)
        self.assertIsInstance(cfg.introductions, IntroductionsConfig)
        self.assertIsInstance(cfg.topic, TopicConfig)

    def test_from_env_defaults(self):
        """from_env() with no env vars set should match pure defaults."""
        env_backup = {}
        env_vars = [
            "LLM_PROVIDER", "OPENAI_BASE_URL", "OPENAI_API_KEY",
            "HF_TOKEN", "SIMILAR_NAMES_MODEL", "TOPIC_MODEL",
        ]
        # Remove any env vars to test defaults
        for var in env_vars:
            env_backup[var] = os.environ.pop(var, None)

        try:
            cfg = TranscriberConfig.from_env()
            self.assertEqual(cfg.llm.provider, "openai")
            self.assertEqual(cfg.llm.openai_base_url, "http://glm-flash.cluster:9999/v1")
            self.assertEqual(cfg.llm.openai_api_key, "not-needed")
            self.assertIsNone(cfg.diarization.hf_token)
            self.assertEqual(cfg.entities.similar_names_model, "glm-4.7-flash")
            self.assertEqual(cfg.topic.topic_model, "glm-4.7-flash")
        finally:
            # Restore env vars
            for var, val in env_backup.items():
                if val is not None:
                    os.environ[var] = val

    def test_from_env_reads_env_vars(self):
        """from_env() should pick up environment variables."""
        os.environ["LLM_PROVIDER"] = "ollama"
        os.environ["HF_TOKEN"] = "test-hf-token"
        os.environ["SIMILAR_NAMES_MODEL"] = "custom-model"
        os.environ["TOPIC_MODEL"] = "my-topic-model"
        try:
            cfg = TranscriberConfig.from_env()
            self.assertEqual(cfg.llm.provider, "ollama")
            self.assertEqual(cfg.diarization.hf_token, "test-hf-token")
            self.assertEqual(cfg.entities.similar_names_model, "custom-model")
            self.assertEqual(cfg.topic.topic_model, "my-topic-model")
        finally:
            del os.environ["LLM_PROVIDER"]
            del os.environ["HF_TOKEN"]
            del os.environ["SIMILAR_NAMES_MODEL"]
            del os.environ["TOPIC_MODEL"]


if __name__ == "__main__":
    unittest.main()
