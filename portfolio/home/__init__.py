from langchain import hub
from django.conf import settings
from langchain.tools import tool
from django.core.cache import cache
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field
from langchain.agents import AgentExecutor
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.utils.function_calling import convert_to_openai_function


class EmailInput(BaseModel):
    message: str = Field(..., description="The message content.")


@tool(args_schema=EmailInput, return_direct=True)
def register_send_email(message: str) -> str:
    """
    Send a message to Nikhil
    """
    cache.set(settings.CHATBOT_MESSAGE_KEY, message)
    return settings.REGISTER_SEND_EMAIL_RETURN

# Langchain RAG settings
AGENT = None
# Embedding function
_EMBEDDING_FUNCTION = OpenAIEmbeddings(model=settings.EMBEDDING_TYPE)
# Pinecone
_PINECONE_VS = PineconeVectorStore(
    index_name=settings.PINECONE_INDEX_NAME, embedding=_EMBEDDING_FUNCTION)
# Search kwargs
__search_kwargs_vs__ = {
    "k": settings.TOP_K,
}
if settings.SEARCH_TYPE == "mmr":
    __search_kwargs_vs__["fetch_k"] = settings.FETCH_K
    __search_kwargs_vs__["lambda_multiplier"] = settings.LAMBDA_MULTIPLIER
# Retriever
_RETRIEVER = _PINECONE_VS.as_retriever(
    search_type=settings.SEARCH_TYPE, search_kwargs=__search_kwargs_vs__)
# Prompt
_PROMPT = hub.pull(settings.LLM_RAG_PROMPT_NAME)
# Tools and function calling
_TOOLS = [
    register_send_email
]
_FUNCTIONS = [convert_to_openai_function(t) for t in _TOOLS]
# LLM
__model_kwargs__ = {
    "top_p": settings.LLM_TOP_P,
    "frequency_penalty": settings.LLM_FREQUENCY_PENALTY,
    "presence_penalty": settings.LLM_PRESENCE_PENALTY,
}
_LLM = ChatOpenAI(
    model=settings.LLM_MODEL_NAME,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKEN_LENGTH,
    **__model_kwargs__
).bind(functions=_FUNCTIONS)
# Chain
_CHAIN = (
    RunnablePassthrough.assign(agent_scratchpad=(
        lambda x: format_to_openai_functions(x["intermediate_steps"])))
    | RunnablePassthrough.assign(context=(lambda x: x["question"]) | _RETRIEVER | (lambda docs: "\n\n".join(doc.page_content for doc in docs)))
    | RunnablePassthrough.assign(question=(lambda x: x["question"]))
    | _PROMPT
    | _LLM
    | OpenAIFunctionsAgentOutputParser()
)
_CHAIN
# Agent
AGENT = AgentExecutor(agent=_CHAIN, tools=_TOOLS, max_iterations=settings.LLM_AGENT_MAX_ITERATIONS, verbose=False)