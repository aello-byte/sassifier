import unittest
from unittest.mock import patch, MagicMock
from extractor.video_ids import VideoIds  


class TestVideoIds(unittest.TestCase):

    @patch("extractor.video_ids.YoutubeDL")
    def test_add_ids(self, mock_youtubedl):
        fake_entries = [
            {"id": "abc123", "title": "UNHhhh Episode 1"},
            {"id": "def456", "title": "UNHhhh Episode 2"},
        ]

        mock_instance = MagicMock()
        mock_instance.__enter__.return_value.extract_info.return_value = {
            "entries": fake_entries
        }
        mock_youtubedl.return_value = mock_instance

        video_ids = VideoIds()
        video_ids.add_ids(query="unhhh", max_results=2)

        assert "abc123" in video_ids.video_ids
        assert "def456" in video_ids.video_ids


if __name__ == "__main__":
    unittest.main()