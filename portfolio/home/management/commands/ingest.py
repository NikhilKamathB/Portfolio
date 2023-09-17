import os
import pickle
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings
from django.core.management.base import BaseCommand, CommandError
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Command(BaseCommand):

    help = "Inject data into a vectorstore using langchain."

    def add_arguments(self, parser):
        parser.add_argument("--data_dir", default="", type=str, help="Path to data directory containing .txt files.")
        parser.add_argument("--output_dir", default="", type=str, help="Path to output directory to store .pkl files.")
        parser.add_argument("--output_file", default="data.pkl", type=str, help="Output pickle file name.")
        parser.add_argument("--chuck_size", default=700, type=int, help="Text splitter chunk size.")
        parser.add_argument("--chunk_overlap", default=100, type=int, help="Text splitter chunk overlap.")
        parser.add_argument("--embedding_model_type", default="openai_embeddings", type=str, help="Embedding model type.")
        parser.add_argument("--embedding_model_name", default="hkunlp/instructor-large", type=str, help="Embedding model name.")
    
    def pickle_txt_data(
            self,
            data_dir: str,
            output_dir:str,
            output_file: str = "data.pkl",
            chuck_size: int = 700,
            chunk_overlap: int = 100,
            embedding_model_type: str = "openai_embeddings", 
            embedding_model_name: str = "hkunlp/instructor-large"):
        loader = DirectoryLoader(data_dir, glob="*.txt")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chuck_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        documents = text_splitter.split_documents(loader.load())
        if embedding_model_type == "openai_embeddings":
            # https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
            embeddings = OpenAIEmbeddings()
        else: # default: huggingface instructor embeddings
            embedding_model_kwargs = {'device': 'cpu'}
            embedding_encode_kwargs = {'normalize_embeddings': True}
            embeddings = HuggingFaceInstructEmbeddings(
                model_name=embedding_model_name,
                model_kwargs=embedding_model_kwargs,
                encode_kwargs=embedding_encode_kwargs
            )
        vectorstore = FAISS.from_documents(documents, embeddings)
        with open(os.path.join(output_dir, output_file), "wb") as f:
            pickle.dump(vectorstore, f)


    def handle(self, *args, **options):
        assert options["data_dir"] != "", "Please provide a data directory path."
        assert options["output_dir"] != "", "Please provide a output directory path."
        data_dir = options["data_dir"]
        output_dir = options["output_dir"]
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                raise CommandError(f"Error creating output directory: {e}")
        self.pickle_txt_data(
            data_dir=data_dir,
            output_dir=output_dir,
            output_file=options["output_file"],
            chuck_size=options["chuck_size"],
            chunk_overlap=options["chunk_overlap"],
            embedding_model_type=options["embedding_model_type"],
            embedding_model_name=options["embedding_model_name"]
        )