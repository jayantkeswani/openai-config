from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

class ScrapperVS:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, html_path) -> None:
        if not self._initialized:
            self.html_path = html_path
            self.raw_documents = TextLoader(self.html_path).load()
            self.html_splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.HTML, chunk_size=500, chunk_overlap=50
            )
            self.html_docs = self.html_splitter.create_documents([self.raw_documents[0].page_content])
            for document in self.html_docs:
                if len(document.metadata) < 1:
                    document.metadata["source"] = "data/data.html"
            self._vector_store = None
            self._initialized = True

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = Chroma.from_documents(self.html_docs, OpenAIEmbeddings())
        return self._vector_store

    def get_response_from_vectorstore(self, question, k=5, max_length=None):
        search_result = self.vector_store._similarity_search_with_relevance_scores(question, k=k, max_length=max_length) if max_length else self.vector_store._similarity_search_with_relevance_scores(question, k=k)
        search_result_list = [result[0].page_content for result in search_result]
        return " ".join(search_result_list)
