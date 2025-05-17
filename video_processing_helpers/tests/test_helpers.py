import unittest


from ..entities import map_entities_to_speakers


class TestTranscriberHelpers(unittest.TestCase):


    def data_map_entities_to_speakers(self):
        diarization_output = [
            {"start": 3.0, "end": 17.1, "speaker": "SPEAKER_01"},        # Doug starts speaking here
            {"start": 17.3, "end": 30.5, "speaker": "SPEAKER_02"},       # Patrick speaking
            {"start": 32, "end": 52.79, "speaker": "SPEAKER_03"},        # Bob speaking
            {"start": 53.23, "end": 71.20, "speaker": "SPEAKER_04"}      # Alice speaks here
        ]

        ner_output = [
            {'start': 5, 'end': 8, 'text': 'Doug', 'label': 'Person', 'score': 0.97},
            {'start': 17.2, 'end': 20, 'text': 'Patrick', 'label': 'Person', 'score': 0.87},
            {'start': 35, 'end': 40, 'text': 'Bob', 'label': 'Person', 'score': 0.90},
            {'start': 60, 'end': 65, 'text': 'Alice Wonderland', 'label': 'Person', 'score': 0.99}
        ]
        return diarization_output, ner_output


    def test_map_entities_to_speakers_margin_1s(self):
        # print("--- With Margin 1.0s ---")            
        diarization_output, ner_output = self.data_map_entities_to_speakers()
        mapped_data_margin = map_entities_to_speakers(None, ner_output, diarization_output, margin=1.0)
        #for item in mapped_data_margin:
        #    print(item)
        expected_result = [
            {'start': 5, 'end': 8, 'text': 'Doug', 'label': 'Person', 'score': 0.97, 'matched_speaker': 'SPEAKER_01', 'overlap_duration': 3},
            {'start': 17.2, 'end': 20, 'text': 'Patrick', 'label': 'Person', 'score': 0.87, 'matched_speaker': 'SPEAKER_02', 'overlap_duration': 2.7},
            {'start': 35, 'end': 40, 'text': 'Bob', 'label': 'Person', 'score': 0.9, 'matched_speaker': 'SPEAKER_03', 'overlap_duration': 5},
            {'start': 60, 'end': 65, 'text': 'Alice Wonderland', 'label': 'Person', 'score': 0.99, 'matched_speaker': 'SPEAKER_04', 'overlap_duration': 5}
            ]
        self.assertListEqual(mapped_data_margin, expected_result)

    def test_map_entities_to_speakers_margin_0_2s(self):
        # print("--- With Margin 0.2s ---")            
        diarization_output, ner_output = self.data_map_entities_to_speakers()
        mapped_data_margin = map_entities_to_speakers(None, ner_output, diarization_output, margin=0.2)
        #for item in mapped_data_margin:
        #    print(item)
        expected_result = [
            {'start': 5, 'end': 8, 'text': 'Doug', 'label': 'Person', 'score': 0.97, 'matched_speaker': 'SPEAKER_01', 'overlap_duration': 3},
            {'start': 17.2, 'end': 20, 'text': 'Patrick', 'label': 'Person', 'score': 0.87, 'matched_speaker': 'SPEAKER_02', 'overlap_duration': 2.7},
            {'start': 35, 'end': 40, 'text': 'Bob', 'label': 'Person', 'score': 0.9, 'matched_speaker': 'SPEAKER_03', 'overlap_duration': 5},
            {'start': 60, 'end': 65, 'text': 'Alice Wonderland', 'label': 'Person', 'score': 0.99, 'matched_speaker': 'SPEAKER_04', 'overlap_duration': 5}
            ]
        self.assertListEqual(mapped_data_margin, expected_result)        
            

    def test_map_entities_to_speakers_margin_exact(self):
        ner_exact_match = [
            {'start': 55.0, 'end': 60.0, 'text': 'Exact Matcher', 'label': 'Person', 'score': 0.9}
            ]
        diarization_exact_match = [
            {"start": 55.0, "end": 60.0, "speaker": "SPEAKER_EXACT"}
            ]
        # print("\n--- Exact Match Test ---")            
        mapped_exact = map_entities_to_speakers(None, ner_exact_match, diarization_exact_match, margin=0.1)
        for item in mapped_exact:
            print(item)
        expected_result = {'start': 55.0, 'end': 60.0, 'text': 'Exact Matcher', 'label': 'Person', 'score': 0.9, 'matched_speaker': 'SPEAKER_EXACT', 'overlap_duration': 5.0}
        self.assertEqual(len(mapped_exact), 1, 
                         f"Expected exactly one item in mapped_exact, got {len(mapped_exact)}")
        self.assertEqual(mapped_exact[0], expected_result, 
                         f"Dictionary mismatch: {mapped_exact[0]} vs {expected_result}")        
            
    def test_map_entities_to_speakers_margin_margin(self):    
        ''' Test case: Entity slightly outside, but within margin '''
        ner_outside_margin = [
        {'start': 72.0, 'end': 75.0, 'text': 'Edge Case', 'label': 'Person', 'score': 0.9}
        ]
        diarization_exact_match = [
            {"start": 55.0, "end": 71.0, "speaker": "SPEAKER"}
        ]        
        mapped_outside = map_entities_to_speakers(None, ner_outside_margin, diarization_exact_match, margin=2.0)
        print("\n--- Edge Case (within margin) Test ---")
        for item in mapped_outside:
             print(item) 
        expected_result = {'start': 72.0, 'end': 75.0, 'text': 'Edge Case', 'label': 'Person', 'score': 0.9, 'matched_speaker': 'SPEAKER', 'overlap_duration': 0.0}             
        self.assertEqual(len(mapped_outside), 1, 
                         f"Expected exactly one item in mapped_exact, got {len(mapped_outside)}")
        self.assertEqual(mapped_outside[0], expected_result, 
                         f"Dictionary mismatch: {mapped_outside[0]} vs {expected_result}")        

    def test_map_entities_to_speakers_margin_outside(self):            
        ''' Test case: Entity completely outside any speaker segment even with margin '''
        ner_no_match = [
        {'start': 100.0, 'end': 105.0, 'text': 'No Speaker Here', 'label': 'Person', 'score': 0.9}
        ]
        diarization_output = [
            {"start": 55.0, "end": 60.0, "speaker": "SPEAKER"}
        ]        
        mapped_no_match = map_entities_to_speakers(None, ner_no_match, diarization_output, margin=1.0)
        print("\n--- No Match Test ---")
        for item in mapped_no_match:
             print(item)
        expected_result = {'start': 100.0, 'end': 105.0, 'text': 'No Speaker Here', 'label': 'Person', 'score': 0.9, 'matched_speaker': None, 'overlap_duration': 0.0}             
        self.assertEqual(len(mapped_no_match), 1, 
                         f"Expected exactly one item in mapped_exact, got {len(mapped_no_match)}")
        self.assertEqual(mapped_no_match[0], expected_result, 
                         f"Dictionary mismatch: {mapped_no_match[0]} vs {expected_result}")        

        
if __name__ == "__main__":
    unittest.main()
