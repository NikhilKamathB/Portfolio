import pickle
from langchain import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores.base import VectorStoreRetriever
from constants import LANGCHAIN_PICKLE_FILE, TEMPLATE, CONDENSED_TEMPLATE, TEMPERATURE, \
    MAX_LENGTH, REPO_ID, MIN_LENGTH, MODEL_NAME, MODEL_TYPE


QA_CONDENSE_PROMPT_TEMPLATE = PromptTemplate.from_template(CONDENSED_TEMPLATE)
QA_PROMPT_TEMPLATE = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])

def load_vectorstore():
    with open(LANGCHAIN_PICKLE_FILE, "rb") as f:
        vectorstore = pickle.load(f)
    return VectorStoreRetriever(vectorstore=vectorstore)

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
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    model = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=QA_CONDENSE_PROMPT_TEMPLATE,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT_TEMPLATE})
    return model

if __name__ == "__main__":
    model = get_custom_prompt_qa_chain()
    ctr = 1
    while True:
        question = input(f"Pass {ctr}: ")
        answer = model({"question": question})
        print(answer['answer'])
        print("\n\n")
        ctr += 1