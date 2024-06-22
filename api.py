import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # Added for CORS support
from langchain_openai import ChatOpenAI
from langchain_community.llms import OpenAI
from langchain_community.callbacks import get_openai_callback
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import Qdrant
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

# .envファイルの内容を読み込む
load_dotenv()

QDRANT_PATH = "./local_qdrant"
COLLECTION_NAME = "my_collection_2"

def build_vector_store(texts):
    qdrant = load_qdrant()
    qdrant.add_texts(texts)

def get_pdf_text(file):
    pdf_reader = PdfReader(file)
    text = '\n\n'.join([page.extract_text() for page in pdf_reader.pages])
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="text-embedding-ada-002",
        chunk_size=500,
        chunk_overlap=0,
    )
    return text_splitter.split_text(text)

def select_model():
    # モデル選択のロジックをここに追加
    return "gpt-3.5-turbo"

def build_qa_model(model):
    qdrant = load_qdrant()
    retriever = qdrant.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )
    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model_name=model),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        verbose=True
    )

def ask(qa_model, query):
    with get_openai_callback() as cb:
        result = qa_model.invoke(query)
        # 必要な情報だけを抽出してシリアライズ可能な形式に変換
        answer = {
            "result": result["result"],
            "source_documents": [
                {"page_content": doc.page_content, "metadata": doc.metadata}
                for doc in result["source_documents"]
            ]
        }
    return answer, cb.total_cost

def load_qdrant():
    client = QdrantClient(path=QDRANT_PATH)
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print('collection created')

    return Qdrant(
        client=client,
        collection_name=COLLECTION_NAME,
        embeddings=OpenAIEmbeddings()
    )

api = Flask(__name__)
CORS(api)  # Added for CORS support

# 既存の関数...

@api.route('/api/upload_pdf', methods=['POST'])
def api_upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        pdf_text = get_pdf_text(file)
        if pdf_text:
            build_vector_store(pdf_text)
            return jsonify({"message": "PDF processed and vector store built"}), 200
        else:
            return jsonify({"error": "Failed to process PDF"}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400

@api.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    model = select_model()
    qa = build_qa_model(model)
    if qa:
        answer, cost = ask(qa, query)
        return jsonify({"answer": answer, "cost": cost}), 200
    else:
        return jsonify({"error": "Failed to build QA model"}), 500

if __name__ == '__main__':
    api.run(port=5000)