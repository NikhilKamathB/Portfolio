import os
import shutil
from typing import Any, List
from django.conf import settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.core.management.base import BaseCommand, CommandError, CommandParser
from home.management.commands.utils import get_embedding_function, EmbeddingType


class Command(BaseCommand):

    help: str = "Ingest data into Chroma DB."
    separator: List[str] = ["\n\n", "\n", "(?<=\. )", " ", ""]
    in_data_glob: str = "*.txt"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--input_directory", default=settings.RAW_DATA_PATH, type=str, help="Directory containing data to ingest.")
        parser.add_argument("-o", "--output_directory", default=settings.CHORMA_DB_PATH, type=str, help="Directory to output data to.")
        parser.add_argument("-c", "--chunk_size", default=settings.CHUNK_SIZE, type=int, help="Text splitter chunk size.")
        parser.add_argument("-co", "--overlap", default=settings.CHUNK_OVERLAP, type=int, help="Text splitter overlap.")
        parser.add_argument("-e", "--embedding_type", default=EmbeddingType.TEXT_EMBEDDING_3_LARGE.value, type=str, help="Embedding type to use - Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002")

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            print("Ingesting data into Chroma DB...")
            # Remove existing chroma db
            if os.path.exists(options["output_directory"]):
                shutil.rmtree(options["output_directory"])
            # Load data
            directory_loader = DirectoryLoader(options["input_directory"], glob=self.in_data_glob, recursive=True)
            data = directory_loader.load()
            # Split data
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=options["chunk_size"], chunk_overlap=options["overlap"], separators=self.separator)
            documents = text_splitter.split_documents(data)
            # Load embedding function
            embedding_function = get_embedding_function(options["embedding_type"])
            # Ingest data
            _ = Chroma.from_documents(
                documents=documents, embedding=embedding_function, persist_directory=options["output_directory"])
            print("Data ingested...")
        except Exception as e:
            raise CommandError(f"An error occurred: `{e}`")