import unittest
from unittest.mock import MagicMock, patch
from main import main
from config import Config

class TestSocialMediaAutomation(unittest.TestCase):

    @patch('google_sheets.GoogleSheetsHandler')
    @patch('content_generator.ContentGenerator')
    @patch('social_connectors.LinkedInConnector')
    @patch('config.Config.validate')
    def test_main_loop_success(self, mock_validate, mock_linkedin, mock_generator, mock_sheets):
        # Setup mocks
        mock_validate.return_value = []
        
        # Mock Sheets data
        mock_sheets_inst = mock_sheets.return_value
        mock_sheets_inst.get_unprocessed_rows.side_effect = [
            [{
                "row_index": 2,
                "data": {
                    "topic": "AI Benefits",
                    "tone": "Professional",
                    "platform": "LinkedIn",
                    "audience": "Tech Leaders"
                }
            }],
            [] # Empty list to break the loop in next iteration or handle manually
        ]
        
        # Mock Generator
        mock_gen_inst = mock_generator.return_value
        mock_gen_inst.generate_post.return_value = "AI is changing the world!"
        
        # Mock Connector
        mock_link_inst = mock_linkedin.return_value
        mock_link_inst.post.return_value = (True, "Posted")

        # We need to catch the loop since main() has while True
        # For testing, we'll patch time.sleep to raise an exception to exit
        with patch('time.sleep', side_effect=InterruptedError("Loop breakthrough")):
            try:
                main()
            except InterruptedError:
                pass

        # Assertions
        mock_sheets_inst.get_unprocessed_rows.assert_called()
        mock_gen_inst.generate_post.assert_called_with({
            "topic": "AI Benefits",
            "tone": "Professional",
            "platform": "LinkedIn",
            "audience": "Tech Leaders"
        })
        mock_sheets_inst.update_row_status.assert_called_with(
            2, "AI is changing the world!", "Posted", unittest.mock.ANY, ""
        )
        print("\n✅ Mock Integration Test Passed!")

if __name__ == "__main__":
    unittest.main()
