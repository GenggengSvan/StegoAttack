import json
import tempfile
import unittest
from pathlib import Path

from Hidden.analysis import ResponseAnalyzer, analyze_json_file
from Hidden.text_hider import analyze_regeneration


class HiddenAnalysisTests(unittest.TestCase):
    def test_penultimate_name_matches_numeric_index(self):
        analyzer = ResponseAnalyzer()
        text = "Morning bright skies. Evening calm seas."

        self.assertEqual(analyzer.extract_words_by_position(text, "penultimate"), ["bright", "calm"])
        self.assertEqual(analyzer.extract_words_by_position(text, -2), ["bright", "calm"])

        record = {"query": "bright calm"}
        analyze_regeneration(record, "query", text, "penultimate")
        self.assertEqual(record["similarity_score"], 1.0)

    def test_acc_excludes_refusals_but_rr_counts_them(self):
        samples = [
            {"query": "alpha beta", "answer_hidden_response": "Alpha goes. Beta stays."},
            {"query": "alpha beta", "answer_hidden_response": "I can't assist with that."},
        ]
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "samples.json"
            input_path.write_text(json.dumps(samples), encoding="utf-8")

            result = analyze_json_file(str(input_path), position="first", modify_original=False)

        self.assertEqual(result["total_samples"], 2)
        self.assertEqual(result["refusal_count"], 1)
        self.assertEqual(result["non_refusal_count"], 1)
        self.assertEqual(result["refusal_rate_percentage"], "50.0%")
        self.assertEqual(result["avg_similarity_score"], 1.0)
        self.assertEqual(result["avg_similarity_percentage"], "100.0%")

    def test_all_refusals_have_zero_acc_without_division_error(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "samples.json"
            input_path.write_text(
                json.dumps([{"query": "alpha beta", "answer_hidden_response": "I can't assist."}]),
                encoding="utf-8",
            )

            result = analyze_json_file(str(input_path), position="first", modify_original=False)

        self.assertEqual(result["non_refusal_count"], 0)
        self.assertEqual(result["refusal_rate_percentage"], "100.0%")
        self.assertEqual(result["avg_similarity_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
