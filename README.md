# Sassifier

**Sassifier** is a Python-based application that . It cleans and segments spoken content into sentences using spaCy’s `en_core_web_sm` model and writes the result to Parquet format for downstream ML or analysis workflows.

---

## Features

- Transcript extraction via `youtube-transcript-api`
- Sentence segmentation using **spaCy's AI model** (`en_core_web_sm`)
- Output in efficient `.parquet` format
- Batched and resumable processing
- Designed for use in ML training pipelines (e.g. LLM fine-tuning)

---
## ⚙️ Setup (Poetry)

1. Install Poetry :

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

or

```bash
pip install poetry 
```

2. Create a virtual environment and install dependencies:

```bash
poetry install
```

**Important**
Download spaCy model for sentence segmentation

```bash
poetry run python -m spacy download en_core_web_sm
```bash


## To-do
- Finish data exploration and train claude model for prediction
- Cloud storage for raw and processed data (AWS S3)
- fastAPI implementation for app interface
- Write unit tests and add GitHub Actions CI
- Maybe : CRON job to refresh data and retrain model
