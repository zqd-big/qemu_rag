import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

PERSIST_DIRECTORY = "data/chroma_db"

class QemuRAG:
    def __init__(self, use_local_llm=False):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
        
        if not os.path.exists(PERSIST_DIRECTORY):
            raise FileNotFoundError(f"Vector DB not found at {PERSIST_DIRECTORY}. Please run ingestion first.")
            
        self.vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embeddings)
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
        
        # Initialize LLM
        # For this demo, we default to OpenAI, but could support Ollama
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             print("Warning: OPENAI_API_KEY not set. Generation might fail if not using local LLM.")
        
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        
        # RAG Prompt
        template = """You are an expert QEMU Simulation Debugging Assistant.
        Use the following context (which includes source code, documentation, and mailing list info) to answer the user's question.
        
        If the context matches a specific error message in the source code, explain WHY it happens based on the C code logic.
        If the answer is not in the context, say you don't know, but try to deduce from similar headers if possible.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query):
        print(f"Querying: {query}")
        return self.chain.invoke(query)

    def retrieve_context(self, query):
        """Returns the raw documents for inspection"""
        return self.retriever.get_relevant_documents(query)
