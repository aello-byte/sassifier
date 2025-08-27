import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import spacy
import os
import logging

class SentenceTransformer:
    def load_spacy_model(self):
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logging.info("Downloading 'en_core_web_sm'...")
            from spacy.cli import download
            download("en_core_web_sm")
            return spacy.load("en_core_web_sm")

    def read_parquet(self, path):
        return pd.read_parquet(path)

    def split_transcripts_to_sentences(self, df, nlp):
        all_rows = []
        for _, row in df.iterrows():
            video_id = row['video_id']
            transcript = row['transcript']
            doc = nlp(transcript)
            for i, sent in enumerate(doc.sents):
                all_rows.append({
                    'video_id': video_id,
                    'sentence': sent.text.strip(),
                    'sentence_index': i
                })
        return pd.DataFrame(all_rows)

    def write_parquet(self, df, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_parquet(output_path, index=False)
        logging.info(f" Wrote {len(df)} rows to {output_path}")

    def transform(self, input_path):
        nlp = self.load_spacy_model()
        df = self.read_parquet(input_path)
        transformed_df = self.split_transcripts_to_sentences(df, nlp)
        return transformed_df
