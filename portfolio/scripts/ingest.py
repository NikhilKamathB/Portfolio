# ref: https://github.com/hwchase17/chat-your-data/blob/master/query_data.py
import pickle
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from constants import LANGCHAIN_DATA_DIR_PATH, LANGCHAIN_PICKLE_FILE


def pickle_txt_data(
        embedding_model_type: str = "openai",
        embedding_model_name: str = "hkunlp/instructor-large",
    ):
    loader = DirectoryLoader(LANGCHAIN_DATA_DIR_PATH, glob="*.txt")
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=600,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False
    )
    documents = text_splitter.split_documents(loader.load())
    if embedding_model_type == "openai":
        # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
        # refer the above link for more details
        embeddings = OpenAIEmbeddings()
    else:
        embedding_model_kwargs = {'device': 'cpu'}
        embedding_encode_kwargs = {'normalize_embeddings': True}
        embeddings = HuggingFaceInstructEmbeddings(
            model_name=embedding_model_name,
            model_kwargs=embedding_model_kwargs,
            encode_kwargs=embedding_encode_kwargs
        )
    vectorstore = FAISS.from_documents(documents, embeddings)
    with open(LANGCHAIN_PICKLE_FILE, "wb") as f:
        pickle.dump(vectorstore, f)

if __name__ == "__main__":
    pickle_txt_data()