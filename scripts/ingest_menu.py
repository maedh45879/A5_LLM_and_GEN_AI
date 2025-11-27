"""
Ingest menu and FAQ documents into a local Chroma vector store.
"""

import argparse

from app.config import get_settings
from app.rag.ingest import ingest_menu


def main():
    parser = argparse.ArgumentParser(description="Ingest menu docs into Chroma.")
    parser.add_argument(
        "--persist-dir",
        type=str,
        default=None,
        help="Override persistence directory for vector store.",
    )
    args = parser.parse_args()

    settings = get_settings()
    vectordb = ingest_menu(settings, args.persist_dir)
    print(
        f"Ingested documents from {settings.rag.menu_dir} into {vectordb._persist_directory}"
    )


if __name__ == "__main__":
    main()
