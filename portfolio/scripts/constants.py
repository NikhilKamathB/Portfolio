LANGCHAIN_DATA_DIR_PATH = "./static_base/data"
LANGCHAIN_PICKLE_FILE = "./static_base/doc/data.pkl"
REPO_ID = "tiiuae/falcon-7b-instruct"
MODEL_TYPE = "openai"
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0
MIN_LENGTH = 100
MAX_LENGTH = 500
TEMPLATE = """You are an AI assistant for answering questions about the Nikhil Bola Kamath.
You are given the following extracted parts of a long document and a question. Provide a conversational answer.
If you don't know the answer, just say "Hmmm, I don't have the answer to this. You may contact Nikhil via email." Don't try to make up an answer.
Question: {question}
=========
{context}
=========
Answer in Markdown:"""
CONDENSED_TEMPLATE = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
You can assume the question about the most recent state of the union address.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""