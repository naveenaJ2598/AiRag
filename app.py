import os
import tempfile

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

st.set_page_config(page_title="LifeDocs AI", page_icon="📁")
st.title("📁 LifeDocs AI")
st.write("Ask questions about your bills, warranties, insurance documents, and manuals.")

@st.cache_resource
def load_models():
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return llm, embeddings

uploaded_files = st.file_uploader(
    "Upload PDF or TXT documents", type=["pdf", "txt"], accept_multiple_files=True
)

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "llm" not in st.session_state:
    st.session_state.llm = None

if st.button("Process Documents"):
    if not uploaded_files:
        st.warning("Please upload at least one document.")
    else:
        all_documents = []
        try:
            with st.spinner("Reading and processing documents..."):
                for uploaded_file in uploaded_files:
                    suffix = os.path.splitext(uploaded_file.name)[1].lower()
                    temp_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                            temp_file.write(uploaded_file.getvalue())
                            temp_path = temp_file.name
                        loader = PyPDFLoader(temp_path) if suffix == ".pdf" else TextLoader(temp_path, encoding="utf-8")
                        docs = loader.load()
                        for doc in docs:
                            doc.metadata["source"] = uploaded_file.name
                        all_documents.extend(docs)
                    finally:
                        if temp_path and os.path.exists(temp_path):
                            os.remove(temp_path)

                if not all_documents:
                    st.warning("No readable text was found in the documents.")
                else:
                    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
                    chunks = splitter.split_documents(all_documents)
                    llm, embeddings = load_models()
                    st.session_state.vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings)
                    st.session_state.llm = llm
                    st.success(f"Processed {len(uploaded_files)} document(s) into {len(chunks)} text chunks.")
        except Exception as error:
            st.error("Document processing failed.")
            st.exception(error)

question = st.text_input("Ask a question about your documents")
if st.button("Ask Question"):
    if st.session_state.vector_store is None:
        st.warning("Please process your documents first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Searching documents and generating an answer..."):
                results = st.session_state.vector_store.similarity_search(question, k=4)
                context = "\n\n".join(
                    f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
                    for doc in results
                )
                prompt = f"""You are LifeDocs AI, a document question-answering assistant.
Answer using ONLY the document context below. If the context does not contain the answer, say: "I could not find this information in the uploaded documents."
Do not invent dates, policy numbers, warranty terms, or amounts. Keep the answer clear and concise.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:"""
                response = st.session_state.llm.invoke(prompt)
                st.subheader("Answer")
                st.write(response.content)
                st.subheader("Sources")
                sources = dict.fromkeys(doc.metadata.get("source", "Unknown") for doc in results)
                for source in sources:
                    st.write(f"- {source}")
        except Exception as error:
            st.error("Could not answer the question.")
            st.exception(error)
