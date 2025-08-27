import logging
from extractor.transcript_generator import TranscriptGenerator
from transformer.file_transformer import FileTransformer

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG
    format="%(levelname)s %(message)s"
)

def main():
    #run extractor
    tsg = TranscriptGenerator()
    tsg.generate_transcripts()
    tsg.generate_transcripts("queens who like to watch")
    tsg.generate_transcripts("ziwe")
    tsg.generate_transcripts("keke palmer")

    #run transformer
    transformer = FileTransformer()
    transformer.transform()





if __name__ == '__main__':
    main()