from yt_dlp import YoutubeDL


class VideoIds:
    def __init__(self):
        self.video_ids = set()

    def search_youtube_videos(self, query, max_results):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,       
            'skip_download': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            info = ydl.extract_info(search_query, download=False)
            return info.get("entries", [])
    
    def add_ids(self,  query="unhhh trixie katya full episode", max_results=30, clear = False):
        entries = self.search_youtube_videos(query, max_results)
        if clear:
            self.video_ids = set()
        
        for entry in entries:
            if entry.get("id") and entry.get("title"):
                self.video_ids.add(entry["id"])





if __name__ == "__main__":
    # results = search_youtube_videos("unhhh trixie katya", max_results=50)
    
    # for video in results:
        # print(f"{video['title']} | {video['id']}")

    video_ids = VideoIds()
    result = video_ids.add_ids("unhhh trixie katya", max_results=100)
    print(video_ids.video_ids)
