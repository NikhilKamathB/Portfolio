import time
from typing import Any, List
from django.conf import settings
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):

    help: str = "Ingest data into Chroma DB."
    separator: List[str] = ["\n\n", "\n", "(?<=\. )", " ", ""]
    in_data_glob: str = "*.txt"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--input_directory", default=settings.RAW_DATA_PATH,
                            type=str, help="Directory containing data to ingest.")
        parser.add_argument("-o", "--output_directory", default=settings.CHORMA_DB_PATH,
                            type=str, help="Directory to output data to.")
        parser.add_argument("-c", "--chunk_size", default=settings.CHUNK_SIZE,
                            type=int, help="Text splitter chunk size.")
        parser.add_argument("-co", "--overlap", default=settings.CHUNK_OVERLAP,
                            type=int, help="Text splitter overlap.")
        parser.add_argument("-e", "--embedding_type", default=settings.EMBEDDING_TYPE, type=str,
                            help="Embedding type to use - Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002")

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            print("#" * 50)
            print("Command Parameters:")
            print(f"Input Directory: {options['input_directory']}")
            print(f"Output Directory: {options['output_directory']}")
            print(f"Chunk Size: {options['chunk_size']}")
            print(f"Chunk Overlap: {options['overlap']}")
            print(f"Embedding Type: {options['embedding_type']}")
            print("#" * 50)
            print("Ingesting data into Pinecone vector store...")
            pc = Pinecone()
            spec = ServerlessSpec(cloud="aws", region="us-east-1") # Free tier - change if you upgrade the plan.
            # Remove existing index
            print("Removing existing index...")
            if settings.PINECONE_INDEX_NAME in pc.list_indexes().names():
                pc.delete_index(settings.PINECONE_INDEX_NAME)
            # Create index
            print("Creating new index...")
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.PINECONE_INDEX_CONFIG[settings.EMBEDDING_TYPE]["dimension"],
                metric=settings.PINECONE_INDEX_CONFIG[settings.EMBEDDING_TYPE]["metric"],
                spec=spec
            )
            # Wait for index to be initialized
            print("Waiting for index to be initialized...")
            while not pc.describe_index(settings.PINECONE_INDEX_NAME).status['ready']:
                time.sleep(1)
            # Load data
            print("Loading data...")
            directory_loader = DirectoryLoader(
                options["input_directory"], glob=self.in_data_glob, recursive=True)
            data = directory_loader.load()
            # Split data
            print("Splitting data...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=options["chunk_size"], chunk_overlap=options["overlap"], separators=self.separator)
            documents = text_splitter.split_documents(data)
            # Load embedding function
            print("Loading embedding function...")
            embedding_function = OpenAIEmbeddings(
                model=options["embedding_type"])
            # Ingest data
            print("Ingesting data...")
            _ = PineconeVectorStore.from_documents(
                documents=documents, embedding=embedding_function, index_name=settings.PINECONE_INDEX_NAME)
            print("Data ingested...")
        except Exception as e:
            raise CommandError(f"An error occurred: `{e}`")