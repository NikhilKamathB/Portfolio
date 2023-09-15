LANGCHAIN_DATA_DIR_PATH = "./static_base/data"
LANGCHAIN_PICKLE_FILE = "./static_base/doc/data.pkl"
REPO_ID = "tiiuae/falcon-7b-instruct"
MODEL_TYPE = "openai"
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 1e-2
MIN_LENGTH = 100
MAX_LENGTH = 500
SEARCH_TOP_K = 6
LAMBDA_MULT = 0.25
CHAIN_TYPE = "stuff"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 3
TEMPLATE = """You are an AI assistant for answering questions about the Nikhil Bola Kamath.
Use the context below to answer the questions.
Try to answer all the questions. You can generate your answers from the context provided to you.
Be very brief in your answers and answer to the point. For example, if the question is "List your projects", you can answer "Project 1, Project 2, Project 3".
Similarly, if the question is "What companies did you work in?", you can answer "Company 1, Company 2, Company 3".
If you don't know the answer, just say "Hmmm, I don't have the answer to this. You may contact Nikhil @ nikhilbolakamath@gmail.com." Don't try to make up an answer.
=========
{context}
=========
Question: {question}
Answer:"""