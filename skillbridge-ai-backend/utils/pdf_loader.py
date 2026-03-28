from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return "\n".join(p.page_content for p in pages)

