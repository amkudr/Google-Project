import unittest
import main


class TestAutoCompletePipelineWithRealZip(unittest.TestCase):
    def setUp(self):
        # Specify the path to your zip file
        self.zip_path = 'Archive2.zip'  # Update with the correct path to your zip file

        # Load data from the zip file
        self.data_store = main.load_data_from_zip(self.zip_path)
        self.inverted_index = main.build_inverted_index(self.data_store)

    def test_full_pipeline_with_real_data(self):
        # Simulate user input
        user_input = 'This is a good'  # Example of user input

        # Get top 5 auto-completions
        suggestions = main.get_top_k_completions(user_input, self.data_store, self.inverted_index, k=5)

        # Check that we received at least one suggestion
        self.assertGreater(len(suggestions), 0, "No suggestions found, but expected at least one")

        # Output the suggestions for visual confirmation
        print(f"Found {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.completed_sentence} (Source: {suggestion.source_text}, Offset: {suggestion.offset}, Score: {suggestion.score})")

if __name__ == '__main__':
    unittest.main()