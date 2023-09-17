from django.conf import settings
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate


class Agent:

    def __init__(self) -> None:
        self.qa_prompt_template = PromptTemplate(template=settings.LANGCHAIN_TEMPLATE, input_variables=["question", "context"])
        self.model_type = settings.LANGCHAIN_MODEL_TYPE
        self.model_name = settings.LANGCHAIN_MODEL_NAME
        self.temperature = settings.LANGCHAIN_MODEL_TEMPERATURE
        self.min_length = settings.LANGCHAIN_MODEL_MIN_LENGTH
        self.max_length = settings.LANGCHAIN_MODEL_MAX_LENGTH
        self.chain_type = settings.LANGCHAIN_CHAIN_TYPE
        self.vectorstore_retriever = settings.LANGCHAIN_VECTORSTORE_RETRIEVER

    def get_qa_chain(self):
        if self.model_type == "openai":
            llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        else:
            llm = HuggingFaceHub(repo_id=self.model_name, model_kwargs={
                # Here, temperature must be positive, > 0
                "temperature": self.temperature,
                "min_length": self.min_length,
                "max_length": self.max_length
            })
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.vectorstore_retriever,
            chain_type=self.chain_type,
            chain_type_kwargs={"prompt": self.qa_prompt_template}
        )
        return qa