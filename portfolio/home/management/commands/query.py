from typing import Any
from django.conf import settings
from langchain_chroma import Chroma
from django.core.management.base import BaseCommand, CommandError, CommandParser
from home.management.commands.utils import get_embedding_function, EmbeddingType

class Command(BaseCommand):

    help: str = "Query Chroma DB."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-i", "--input_directory", default=settings.CHORMA_DB_PATH, type=str, help="Directory containing Chroma DB.")
        parser.add_argument("-q", "--query", default="What is the meaning of life?", type=str, help="Query to run.")
        parser.add_argument("-k", "--top_k", default=settings.TOP_K, type=int, help="Number of results to return.")
        parser.add_argument("-e", "--embedding_type", default=EmbeddingType.TEXT_EMBEDDING_3_LARGE.value, type=str,
                            help="Embedding type to use - Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002")
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            print("Querying Chroma DB...")
            # Get embedding function
            embedding_function = get_embedding_function(options["embedding_type"])
            # Load Chroma DB
            db = Chroma(
                persist_directory=options["input_directory"], embedding_function=embedding_function)
            # Query Chroma DB
            results = db.similarity_search_with_score(query=options["query"], k=options["top_k"])
            print(f"Results: {results}")
            print("Querying Chroma DB done...")
        except Exception as e:
            raise CommandError(f"An error occurred: `{e}`")