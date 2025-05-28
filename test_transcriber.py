import unittest
import os


from mst import VideoTranscriber
from mst.steps import clear_cache_directory
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
    "MIN_SEGMENT_SIZE": 2,
    "LAMBDA_BALANCE": 0,
    "UTTERANCE_EXPANSION_WIDTH": 2,
    "EMBEDDINGS": embeddings_config,
    "TEXT_KEY": "transcript"
}


class TestTranscriber(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setup tests."""
        cls.transcriber = VideoTranscriber(config)
        cls.path = "data/5rmAy8fgYsY_audio.wav"
        cls.transcriber.clear(cls.path)
    
    def test_transcribe(self):
        result, nouns_list = self.transcriber.transcribe_video(self.path)
        self.assertTrue(len(result) > 1)

    def test_topics(self):
        result, nouns_list = self.transcriber.transcribe_video(self.path)        
        result, headlines, summary = self.transcriber.topics(self.path, result, 5)    
        self.transcriber.format_transcript(self.path, result, nouns_list, headlines, summary)
        
    def test_output(self):
        result, nouns_list = self.transcriber.transcribe_video(self.path)        
        result, headlines, summary = self.transcriber.topics(self.path, result, 5)    
        self.transcriber.format_transcript(self.path, result, nouns_list, headlines, summary)
        self.assertIsNotNone(self.transcriber.retrieve_json)
        self.assertIsNotNone(self.transcriber.retrieve_markdown)        
        

if __name__ == "__main__":
    unittest.main()
