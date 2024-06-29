import os
import shutil
from enum import Enum
from typing import Any, List
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.core.management.base import BaseCommand, CommandError, CommandParser


class EmbeddingType(Enum):

    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class Command(BaseCommand):

    help: str = "Ingest data into Chroma DB."
    separator: List[str] = ["\n\n", "\n", "(?<=\. )", " ", ""]
    in_data_glob: str = "*.txt"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--input_directory", default="./static_base/data", type=str, help="Directory containing data to ingest.")
        parser.add_argument("-o", "--output_directory", default="./static_base/chroma_db", type=str, help="Directory to output data to.")
        parser.add_argument("-c", "--chunk_size", default=4000, type=int, help="Text splitter chunk size.")
        parser.add_argument("-co", "--overlap", default=200, type=int, help="Text splitter overlap.")
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
            # Load embeddings
            if options["embedding_type"] == EmbeddingType.TEXT_EMBEDDING_3_SMALL.value:
                embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            elif options["embedding_type"] == EmbeddingType.TEXT_EMBEDDING_3_LARGE.value:
                embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            elif options["embedding_type"] == EmbeddingType.TEXT_EMBEDDING_ADA_002.value:
                embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
            else:
                raise NotImplementedError(f"Embedding type {options['embedding_type']} not implemented.")
            embeddings = OpenAIEmbeddings(model=options["embedding_type"])
            # Ingest data
            _ = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=options["output_directory"])
            print("Data ingested...")
        except Exception as e:
            raise CommandError(f"An error occurred: `{e}`")