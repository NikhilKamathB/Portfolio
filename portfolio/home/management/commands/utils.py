from enum import Enum
from langchain_openai import OpenAIEmbeddings


def get_embedding_function(embedding_type: str) -> OpenAIEmbeddings:
    if embedding_type == EmbeddingType.TEXT_EMBEDDING_3_SMALL.value:
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif embedding_type == EmbeddingType.TEXT_EMBEDDING_3_LARGE.value:
        return OpenAIEmbeddings(model="text-embedding-3-large")
    elif embedding_type == EmbeddingType.TEXT_EMBEDDING_ADA_002.value:
        return OpenAIEmbeddings(model="text-embedding-ada-002")
    else:
        raise NotImplementedError(f"Embedding type {embedding_type} not implemented.")


class EmbeddingType(Enum):

    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"


class SearchType(Enum):

    MMR = "mmr"
    SIMILARITY_SCORE_THRESHOLD = "similarity_score_threshold"
