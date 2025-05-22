import unittest


from mst import VideoTranscriber
from mst.steps import clear_cache_directory

class TestTranscriber(unittest.TestCase):

    def test_ingestion(self):
        path = "data/5rmAy8fgYsY_audio.wav"
        clear_cache_directory(path)
        transcriber = VideoTranscriber()
        result = transcriber.transcribe_video(path)
        self.assertTrue(len(result) > 1)

if __name__ == "__main__":
    unittest.main()
