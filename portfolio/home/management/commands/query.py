from typing import Any
from django.conf import settings
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):

    help: str = "Query Pinecone DB."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--input_directory", default=settings.CHORMA_DB_PATH,
                            type=str, help="Directory containing Pinecone DB.")
        parser.add_argument(
            "-q", "--query", default="What is the meaning of life?", type=str, help="Query to run.")
        parser.add_argument("-k", "--top_k", default=settings.TOP_K,
                            type=int, help="Amount of documents to return (Default: 4)")
        parser.add_argument("-fk", "--fetch_k", default=settings.FETCH_K, type=int,
                            help="Amount of documents to pass to MMR algorithm (Default: 20)")
        parser.add_argument("-l", "--lambda_multiplier", default=settings.LAMBDA_MULTIPLIER, type=float,
                            help="Lambda multiplier for MMR algorithm (Default: 0.5 | 0.0 = only similarity, 1.0 = only diversity)")
        parser.add_argument("-e", "--embedding_type", default=settings.EMBEDDING_TYPE, type=str,
                            help="Embedding type to use - Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002")
        parser.add_argument("-s", "--search_type", default=settings.SEARCH_TYPE, type=str,
                            help="Search type to use - Options: mmr, similarity_score_threshold")

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            print("#" * 50)
            print("Command Parameters:")
            print(f"Input Directory: {options['input_directory']}")
            print(f"Query: {options['query']}")
            print(f"Top K: {options['top_k']}")
            print(f"Fetch K: {options['fetch_k']}")
            print(f"Lambda Multiplier: {options['lambda_multiplier']}")
            print(f"Embedding Type: {options['embedding_type']}")
            print(f"Search Type: {options['search_type']}")
            print("#" * 50)
            print("Querying Pinecone vector store...")
            # Get embedding function
            embedding_function = OpenAIEmbeddings(
                model=options["embedding_type"])
            # Load Pinecone vector store
            pinecone_vs = PineconeVectorStore(
                index_name=settings.PINECONE_INDEX_NAME, embedding=embedding_function)
            # Retriever for Pinecone vector store
            search_kwargs = {}
            search_kwargs["k"] = options["top_k"]
            if options["search_type"] == "mmr":
                search_kwargs["fetch_k"] = options["fetch_k"]
                search_kwargs["lambda_multiplier"] = options["lambda_multiplier"]
            retreiver = pinecone_vs.as_retriever(
                search_type=options["search_type"],
                search_kwargs=search_kwargs
            )
            # Get results
            results = retreiver.invoke(options["query"])
            print(f"Results: {results}")
            print("Querying Pinecone DB done...")
        except Exception as e:
            raise CommandError(f"An error occurred: `{e}`")