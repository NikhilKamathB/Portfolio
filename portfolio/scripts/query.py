import pickle
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores.base import VectorStoreRetriever
from constants import LANGCHAIN_PICKLE_FILE, TEMPLATE, TEMPERATURE, CHAIN_TYPE, LAMBDA_MULT, \
    MAX_LENGTH, REPO_ID, MIN_LENGTH, MODEL_NAME, MODEL_TYPE, SEARCH_TOP_K


QA_PROMPT_TEMPLATE = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])

def load_vectorstore():
    with open(LANGCHAIN_PICKLE_FILE, "rb") as f:
        vectorstore = pickle.load(f)
    return VectorStoreRetriever(vectorstore=vectorstore, search_type="mmr", search_kwargs={"top_k": SEARCH_TOP_K, "lambda_mult": LAMBDA_MULT})

def get_custom_prompt_qa_chain():
    if MODEL_TYPE == "openai":
        llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)
    else:
        llm = HuggingFaceHub(repo_id=REPO_ID, model_kwargs={
            # Here, temperature must be positive, > 0
            "temperature": TEMPERATURE,
            "min_length": MIN_LENGTH,
            "max_length": MAX_LENGTH
        })
    retriever = load_vectorstore()
    model = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type=CHAIN_TYPE,
        chain_type_kwargs={"prompt": QA_PROMPT_TEMPLATE})
    return model

if __name__ == "__main__":
    model = get_custom_prompt_qa_chain()
    ctr = 1
    while True:
        query = input(f"Pass {ctr}: ")
        answer = model({"query": query})
        print(answer)
        print("\n\n")
        ctr += 1