import pyarrow as pa
import pyarrow.parquet as pq
import os
import re

data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
os.makedirs(data_dir, exist_ok=True)
"""
BASE Classes
"""
#df to parquet
class ParquetWriter:
    def __init__(self, output_dir, file_name):
        self.output_dir = output_dir
        self.file_name = file_name
        self.file_index = self._get_next_file_index()

        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    
    def write(self, df):
        file_path = os.path.join(self.output_dir, f"{self.file_name}-{self.file_index:04}.parquet")
        df.to_parquet(file_path, index=False)

    def _get_next_file_index(self):
        files = os.listdir(self.output_dir)
        pattern = re.compile(rf"{re.escape(self.file_name)}-(\d{4})\.parquet")
        indices = [
            int(match.group(1))
            for file in files
            if (match := pattern.match(file))
        ]
        return max(indices) + 1 if indices else 0

#python dict list to parquet
#caps row number
class RotatingParquetWriter:
    def __init__(self, output_dir, file_name, schema, max_rows_per_file=100_000):
        self.output_dir = output_dir
        self.file_name = file_name
        self.schema = schema
        self.max_rows = max_rows_per_file
        self.buffer = []
        self.video_ids = set()
        self.file_index = self._get_next_file_index()

        os.makedirs(output_dir, exist_ok=True)
    
    def _get_next_file_index(self):
        files = os.listdir(self.output_dir)
        pattern = re.compile(rf"{re.escape(self.file_name)}-(\d{4})\.parquet")
        indices = [
            int(match.group(1))
            for file in files
            if (match := pattern.match(file))
        ]
        return max(indices) + 1 if indices else 0

    def _write_buffer(self):
        if not self.buffer:
            return set()
        table = pa.Table.from_pylist(self.buffer, schema=self.schema)
        file_path = os.path.join(self.output_dir, f"{self.file_name}-{self.file_index:04}.parquet")
        pq.write_table(table, file_path, compression="snappy")
        print(f"Wrote {len(self.buffer)} rows to {file_path}")
        
        flushed_ids = self.video_ids.copy()

        self.buffer.clear()
        self.video_ids.clear()
        self.file_index += 1

        return flushed_ids

    def write(self, rows, video_id):
        if len(self.buffer) + len(rows) > self.max_rows:
            flushed = self._write_buffer()
        else:
            flushed = set()

        self.buffer.extend(rows)
        self.video_ids.add(video_id)

        return flushed
    
    def flush(self):
        return self._write_buffer()

    def close(self):
        return self.flush()

"""
Schema-specific classes that inherit base classes
"""
class RawParquetWriter(RotatingParquetWriter):
    def __init__(self, max_rows_per_file=1000):
        schema = pa.schema([
            ("video_id", pa.string()),
            ("original_url", pa.string()),
            ("transcript", pa.string())
        ])
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
        file_name = "tscript"
        os.makedirs(output_dir, exist_ok=True)
        super().__init__(output_dir=output_dir, file_name=file_name, schema=schema, max_rows_per_file=max_rows_per_file)

class TransformedParquetWriter(ParquetWriter):
    def __init__(self):
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transformed')
        file_name = "transformed_data"
        super().__init__(output_dir=output_dir, file_name=file_name)