
import os
import re
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from document_preprocess.documents_loader import DocumentLoader
from document_preprocess.text_splitter import TextSplitter

class Chunk:
    def __init__(self, ch_size: int = 1024):
        openai_api_key =  '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'
        self.ch_size = ch_size
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0.1)

        document_loader = DocumentLoader(path="./RAG-Documents")
        documents = document_loader.load_documents()

        splitter = TextSplitter()
        chunks = splitter.split_docs(documents)
        documents = [Document(page_content=str(chunk)) for chunk in chunks]
        self.documents = documents

        embeddings = OpenAIEmbeddings(api_key=openai_api_key, model='text-embedding-3-large')
        self.db = FAISS.from_documents(documents, embeddings)

        # Initialize memory for user
        self.user_memory = {}

    def load_pdf(self, path: str):
        """Load and process PDF files."""
        document_loader = DocumentLoader(path=path)
        documents = document_loader.load_documents()

        splitter = TextSplitter()
        chunks = splitter.split_docs(documents)
        new_documents = [Document(page_content=str(chunk)) for chunk in chunks]

        self.documents.extend(new_documents)
        self.db.add_documents(new_documents)

    def save_to_memory(self, user_id: str, message: str, max_memory_size: int = 10):
        """Сохранить сообщение в память по идентификатору пользователя с ограничением размера."""
        if user_id not in self.user_memory:
            self.user_memory[user_id] = []
        
        # Добавить новое сообщение
        self.user_memory[user_id].append(message)
        
        # Обрезать память, если она превышает лимит
        if len(self.user_memory[user_id]) > max_memory_size:
            self.user_memory[user_id].pop(0)  # Удалить самое старое сообщение
        
        print(f"Сохранено в память: {user_id}, {message}")  # Отладочный вывод

    def get_combined_memory(self, user_id: str):
        """Retrieve chat history for the user."""
        return self.user_memory.get(user_id, [])

    async def async_get_answer(self, query: str = None, user_id: str = None):
        """Get answer considering the user's chat history."""
        system_prompt = """
        Ты учитель по китайскому языку, отвечай на вопросы ученика на основе документов с информацией. 
        Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией 
        для ответа ученику.
        
        """

        # Retrieve chat history for the user
        history = self.get_combined_memory(user_id)
        history_text = "\n".join(history)
        
        docs = self.db.similarity_search(query, k=4)
        message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))

        combined_input = f"История чата:\n{history_text}\n\nТекущий вопрос:\n{query}\n\nДокумент с информацией:\n{message_content}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])
        output_parser = StrOutputParser()
        chain = prompt | self.llm | output_parser 

        answer = chain.invoke({"input": combined_input})

        # Save current interaction to memory
        self.save_to_memory(user_id, f"Вопрос: {query}\nОтвет: {answer}")

        return answer