from pathlib import Path
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import Settings


def _build_loader(path: Path) -> DirectoryLoader:
    """
    Loader that supports txt, md, pdf. PDFs use PyPDFLoader.
    """
    glob = "**/*"
    loader_kwargs = {"loader_cls": TextLoader, "loader_kwargs": {"encoding": "utf-8"}}
    return DirectoryLoader(str(path), glob=glob, show_progress=True, **loader_kwargs)


def _pdf_loader(path: Path) -> DirectoryLoader:
    return DirectoryLoader(str(path), glob="**/*.pdf", loader_cls=PyPDFLoader)


def get_splitter(settings: Settings) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.rag.chunk_size,
        chunk_overlap=settings.rag.chunk_overlap,
        add_start_index=True,
    )


def build_embeddings() -> HuggingFaceEmbeddings:
    # Small, CPU-friendly embedding model that works offline.
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def ingest_menu(settings: Settings, persist_directory: Optional[Path] = None) -> Chroma:
    """
    Ingest menu/FAQ docs into a persistent Chroma store.
    """
    menu_dir = settings.rag.menu_dir
    persist_dir = Path(persist_directory or settings.rag.vector_store_path)
    persist_dir.mkdir(parents=True, exist_ok=True)

    text_loader = _build_loader(menu_dir)
    pdf_loader = _pdf_loader(menu_dir)
    docs = text_loader.load() + pdf_loader.load()

    splitter = get_splitter(settings)
    splits = splitter.split_documents(docs)
    embeddings = build_embeddings()
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    vectordb.persist()
    return vectordb


def load_retriever(settings: Settings) -> Optional[Chroma]:
    persist_dir = Path(settings.rag.vector_store_path)
    if not persist_dir.exists():
        return None
    embeddings = build_embeddings()
    return Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
    )
