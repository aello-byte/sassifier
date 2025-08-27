import unittest
from extractor.video_ids import VideoIds


class TestVideoIdsIntegration(unittest.TestCase):

    def test_real_youtube_query_returns_results(self):
        video_ids = VideoIds()
        video_ids.add_ids(query="unhhh trixie katya", max_results=5)

        print("Retrieved video IDs:", video_ids.video_ids)

        self.assertGreater(len(video_ids.video_ids), 0)
        for vid in video_ids.video_ids:
            self.assertIsInstance(vid, str)
            self.assertRegex(vid, r"^[\w-]{11}$")  # YouTube IDs are 11-character strings


if __name__ == "__main__":
    unittest.main()