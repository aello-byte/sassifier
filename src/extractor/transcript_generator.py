from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from tqdm import tqdm


import logging
import requests
import re
import os
import threading
from dotenv import load_dotenv

from extractor.video_ids import VideoIds
from writer.parquet_writer import RawParquetWriter
from utils.processed_data import load_processed_ids, save_processed_ids

load_dotenv()  # Looks for .env at root 
processed = load_processed_ids()

MAX_CONCURRENT_FETCHES = 8
fetch_semaphore = threading.Semaphore(MAX_CONCURRENT_FETCHES)

class TranscriptGenerator:
    def __init__(self):
        self.parquet_writer = RawParquetWriter()
        proxy_user = os.getenv("PROXY_USER")
        proxy_pass = os.getenv("PROXY_PASS")
        self.ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )
        self.video_ids = VideoIds()

    def clean_transcript(self, transcript):
        """
        joining transcript text, removing whitespace and timestamps
        """
        raw_data = transcript.to_raw_data()
        raw_data.sort(key=lambda x: x['start']) #ensure strict time ordering 
        cleaned = " ".join([entry['text'] for entry in raw_data])
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=1000),
    retry=retry_if_exception_type((requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError)),
    before_sleep=before_sleep_log(logging, logging.WARNING),
    reraise=True,  
    )
    def fetch(self, video_id : str):
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        return self.ytt_api.fetch(video_id=video_id, languages=['en'])


    def fetch_and_prepare_transcript(self, video_id : str):
        try:
            transcript = self.fetch(video_id)
            cleaned = self.clean_transcript(transcript)
            rows = [
                {
                    "video_id": video_id,
                    "original_url": f"https://www.youtube.com/watch?v={video_id}",
                    "transcript": cleaned
                }
            ]
            return rows
        except Exception as e:
            logging.warning(f"Skipping video {video_id}: {e}")
            return None  
        
        
    def retrieve_video_ids(self, search_query : str):
        try:
            logging.info(f"Retrieving video ids.")
            self.video_ids.add_ids(search_query, max_results=10000)
            logging.info(f"Retrieved {len(self.video_ids.video_ids)} from search.")
        except Exception as e:
            logging.exception(f"Failed to fetch video ids based on query {search_query}")

    def _process_single_video_id(self, video_id: str) -> set:
        if video_id in processed:
            return set()

        rows = self.fetch_and_prepare_transcript(video_id)
        if rows:
            flushed = self.parquet_writer.write(rows, video_id)
            return flushed
        return set()

    def process_video_ids(self, max_workers: int = 8):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._process_single_video_id, vid): vid
                for vid in self.video_ids.video_ids
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="fetching transcripts"):
                flushed_ids = future.result()
                if flushed_ids:
                    processed.update(flushed_ids)
                    save_processed_ids(processed)

        remaining_ids = self.parquet_writer.close()
        if remaining_ids:
            processed.update(remaining_ids)
            save_processed_ids(processed)

    def generate_transcripts(self, search_query: str = "unhhh trixie katya"):
        self.retrieve_video_ids(search_query)
        self.process_video_ids()



    