import glob
import pandas as pd
from transformer.sentence_transformer import SentenceTransformer
from writer.parquet_writer import TransformedParquetWriter

class FileTransformer:
    def __init__(self):
        self.parquet_files = glob.glob("data/raw/*.parquet")
        self.transformer = SentenceTransformer()
        self.writer = TransformedParquetWriter()

    def transform(self):
        for file_path in self.parquet_files:
            transformed = self.transformer.transform(file_path)
            self.writer.write(transformed)

