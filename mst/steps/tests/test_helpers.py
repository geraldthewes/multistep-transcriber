import unittest


from ..introductions import map_entities_to_speakers
from ..merge_sentences import merge_transcript_segments, _map_sentences_to_segments
from ..helpers import compress_transcript

class TestMapSpeakers(unittest.TestCase):


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
        #for item in mapped_exact:
        #    print(item)
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
        # print("\n--- Edge Case (within margin) Test ---")
        #for item in mapped_outside:
        #     print(item) 
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
        # print("\n--- No Match Test ---")
        #for item in mapped_no_match:
        #     print(item)
        expected_result = {'start': 100.0, 'end': 105.0, 'text': 'No Speaker Here', 'label': 'Person', 'score': 0.9, 'matched_speaker': None, 'overlap_duration': 0.0}             
        self.assertEqual(len(mapped_no_match), 1, 
                         f"Expected exactly one item in mapped_exact, got {len(mapped_no_match)}")
        self.assertEqual(mapped_no_match[0], expected_result, 
                         f"Dictionary mismatch: {mapped_no_match[0]} vs {expected_result}")        


    def test_diarization_off(self):
        transcript = [
            {
                "start": 2751.5699999999997,
                "end": 2758.8,
                "transcript": "If you could state your name, address,any relevant boards or committees,and how you'd like the board to address you."
            },
            {
                "start": 2758.8,
                "end": 2761.2700000000004,
                "transcript": "Thank you."
            },
            {
                "start": 2761.2700000000004,
                "end": 2764.78,
                "transcript": "I'm Patrick Mayor, 31 Woodcliff Road, Precinct 3.You did not miss me."
            },
            {
                "start": 2764.78,
                "end": 2768.78,
                "transcript": "I took all this time to figure out technicallyhow to raise electronically my hand."
            },
            {
                "start": 2768.78,
                "end": 2770.67,
                "transcript": "I just didn't know how to do it.do it."
            },
            {
                "start": 2770.67,
                "end": 2774.48,
                "transcript": "So my apologies and my thanks for allowing me to speak briefly."
            },
            {
                "start": 2774.48,
                "end": 2774.48,
                "transcript": "No worries."
            }
        ]
        diarization_output = [
            {
                "start": 2751.24659375,
                "end": 2753.3222187500005,
                "speaker": "SPEAKER_05"
            },
            {
                "start": 2754.36846875,
                "end": 2755.2965937500003,
                "speaker": "SPEAKER_05"
            },
            {
                "start": 2755.56659375,
                "end": 2761.48971875,
                "speaker": "SPEAKER_05"
            },
            {
                "start": 2762.6540937500004,
                "end": 2776.37346875,
                "speaker": "SPEAKER_00"
            }
        ]
        speaker_map =  map_entities_to_speakers(None, transcript, diarization_output, margin=1.0)
        # print(speaker_map)
        self.assertEqual(speaker_map[0]['matched_speaker'],'SPEAKER_05')
        self.assertEqual(speaker_map[2]['matched_speaker'],'SPEAKER_00')        

            
        
from ..merge_sentences import merge_transcript_segments
        
class TestTranscriberSentences(unittest.TestCase):

    def segments_no_change(self):
        transcript = [
            {
                "start": 0.0,
                "end": 10.0,
                "transcript": "Okay, good evening."
            },
            {
                "start": 30.0,
                "end": 35.76,
                "transcript": "on Monday, April 28th, 2025, and I call this open meeting of the Lexington Select Board to order."
            },
            {
                "start": 36.4,
                "end": 39.94,
                "transcript": "This evening's meeting is being conducted in a hybrid format via Zoom."
            },
            {
                "start": 40.480000000000004,
                "end": 45.92,
                "transcript": "Members of the public can view and participate in the meeting from their devices by clicking on the link posted with the agenda."
            },
            {
                "start": 46.58,
                "end": 48.54,
                "transcript": "Please note that the meeting is being recorded."
            },
            {
                "start": 48.74,
                "end": 52.44,
                "transcript": "We're also being broadcast live and for future on-demand viewing by Lex Media."
            },
            {
                "start": 53.260000000000005,
                "end": 56.879999999999995,
                "transcript": "All materials provided to members of the board are also available to the public."
            },
            {
                "start": 57.519999999999996,
                "end": 59.94,
                "transcript": "Members of the board are in person this evening."
            }
        ]       
        return transcript 
    

    def test_map_sentences(self):
        transcript = self.segments_no_change()
        sentences = ['Okay, good evening.', 'on Monday, April 28th, 2025, and I call this open meeting of the Lexington Select Board to order.', "This evening's meeting is being conducted in a hybrid format via Zoom.", 'Members of the public can view and participate in the meeting from their devices by clicking on the link posted with the agenda.', 'Please note that the meeting is being recorded.', "We're also being broadcast live and for future on-demand viewing by Lex Media.", 'All materials provided to members of the board are also available to the public.', 'Members of the board are in person this evening.']
        cumulative_lengths = [0, 19, 116, 186, 314, 361, 439, 519, 567]
        merged_segments = _map_sentences_to_segments(sentences, transcript, cumulative_lengths)
        #print(merged_segments)
        self.assertEqual(transcript, merged_segments)        
        
    
    def test_sentence_merge(self):
        transcript = self.segments_no_change()
        # First two records will be merged
        merged_transcript = merge_transcript_segments(None, transcript)
        #print(merged_transcript)
        self.assertEqual(transcript[2:-1], merged_transcript[1:-1])


class TestTranscriberCompress(unittest.TestCase):

    def test_compress_speaker(self):
        transcript = [
            {
                "start": 2761.2700000000004,
                "end": 2761.48971875,
                "transcript": "I'm Patrick Mayor 31 Woodcliff Road, Precinct 3.You did not miss me.",
                "speaker": "SPEAKER_05",
                "duration": 0.21971874999962893
            },
            {
                "start": 2761.48971875,
                "end": 2764.78,
                "transcript": "I'm Patrick Mayor 31 Woodcliff Road, Precinct 3.You did not miss me.",
                "speaker": "SPEAKER_00",
                "duration": 3.2902812500001346
            }
        ]
        compressed = compress_transcript(None, transcript)
        self.assertEqual(compressed[0],     {
            "start": 2761.2700000000004,
            "end": 2764.78,
            "transcript": "I'm Patrick Mayor 31 Woodcliff Road, Precinct 3.You did not miss me.",
            "speaker": "SPEAKER_00",
            "duration": 3.51})

    

        
if __name__ == "__main__":
    unittest.main()
