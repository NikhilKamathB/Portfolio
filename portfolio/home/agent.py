from django.conf import settings
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from home.tools import GoogleCalendarEventGeneratorTool

class Agent:

    def __init__(self, verbose=False):
        self.model_type = settings.LANGCHAIN_MODEL_TYPE
        self.model_name = settings.LANGCHAIN_MODEL_NAME
        self.temperature = settings.LANGCHAIN_MODEL_TEMPERATURE
        self.min_length = settings.LANGCHAIN_MODEL_MIN_LENGTH
        self.max_length = settings.LANGCHAIN_MODEL_MAX_LENGTH
        self.chain_type = settings.LANGCHAIN_CHAIN_TYPE
        self.vectorstore_retriever = settings.LANGCHAIN_VECTORSTORE_RETRIEVER
        self.qa_prompt_template = PromptTemplate(template=settings.LANGCHAIN_TEMPLATE, input_variables=["question", "context"])
        self.verbose = verbose
        self.__get_llm(); self.__get_tools()
    
    def __get_llm(self):
        if self.model_type == "openai":
            self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        else:
            self.llm = HuggingFaceHub(repo_id=self.model_name, model_kwargs={
                # Here, temperature must be positive, > 0
                "temperature": self.temperature,
                "min_length": self.min_length,
                "max_length": self.max_length
            })

    def __get_tools(self):
        self.tools = [
            GoogleCalendarEventGeneratorTool()
        ]

    def get_qa_chain(self):
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vectorstore_retriever,
            chain_type=self.chain_type,
            chain_type_kwargs={"prompt": self.qa_prompt_template}
        )
        return qa

    def get_qa_agent_with_memory_chain(self):
        if settings.LANGCHAIN_CHAIN_AGENT_DOMAIN_SPECIFIC_QUERY:
            qa = self.get_qa_chain()
            self.tools.append(Tool(
                name="nkb_info_retrieval_qa_tool",
                func=qa.run,
                description=settings.LANGCHAIN_NBK_QA_TOOL_DESC
            ))
        conversational_memory = ConversationBufferWindowMemory(
            memory_key=settings.LANGCHAIN_CONVERSATIONAL_BUFFER_WINDOW_MEMORY_KEY,
            k=settings.LANGCHAIN_CONVERSATIONAL_BUFFER_WINDOW_MEMORY_K,
            return_messages=True
        )
        qa_agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            max_iterations=settings.LANGCHAIN_CHAIN_AGENT_MAX_ITERATIONS,
            # for agent="chat-conversational-react-description"
            agent=settings.LANGCHAIN_CHAIN_AGENT_CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            # for agent="structured-chat-zero-shot-react-description"
            # agent=settings.LANGCHAIN_CHAIN_AGENT_STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, 
            verbose=self.verbose if self.verbose else settings.LANGCHAIN_CHAIN_AGENT_VERBOSE,
            early_stopping_method=settings.LANGCHAIN_CHAIN_AGENT_EARLY_STOP,
            memory=conversational_memory
        )
        qa_agent.agent.llm_chain.prompt = qa_agent.agent.create_prompt(
            # `system_message` use this when agent="chat-conversational-react-description"
            system_message=settings.LANGCHAIN_AGENT_SYSTEM_MESSAGE_CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            # `prefix`, `format_instructions` and `suffix` use this when agent="structured-chat-zero-shot-react-description"
            # prefix=settings.LANGCHAIN_AGENT_SYSTEM_MESSAGE_STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION_PREFIX,
            # format_instructions=settings.LANGCHAIN_AGENT_SYSTEM_MESSAGE_STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION_FORMAT_INSTRUCTIONS,
            # suffix=settings.LANGCHAIN_AGENT_SYSTEM_MESSAGE_STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION_SUFFIX,
            tools=self.tools
        )
        if self.verbose: print(qa_agent.agent.llm_chain.prompt.messages[0].prompt.template)
        return qa_agent