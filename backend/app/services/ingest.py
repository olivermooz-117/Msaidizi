from pypdf import PdfReader
from io import BytesIO
from backend.app.extensions import db
from backend.app.models import Document, Chunk
from backend.app.llm import embed_texts


def chunk_text(text: str, max_chars: int = 450) -> list[str]:
    paragraphs = [p.strip() for p in text.replace("\r", "").split("\n\n") if p.strip()]
    chunks = []
    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            words = para.split()
            current = []
            for w in words:
                current.append(w)
                if len(" ".join(current)) > max_chars:
                    chunks.append(" ".join(current[:-1]))
                    current = [w]
            if current:
                chunks.append(" ".join(current))
    return chunks


def ingest_text(business_id: str, title: str, text: str, source_type: str = "paste") -> Document:
    doc = Document(business_id=business_id, title=title, source_type=source_type)
    db.session.add(doc)
    db.session.flush()

    pieces = chunk_text(text)
    if not pieces:
        db.session.commit()
        return doc

    embeddings = embed_texts(pieces)

    for i, (piece, emb) in enumerate(zip(pieces, embeddings)):
        chunk = Chunk(
            document_id=doc.id,
            text=piece,
            embedding=emb,
            position=i,
        )
        db.session.add(chunk)

    db.session.commit()
    return doc


def ingest_pdf(business_id: str, title: str, file_bytes: bytes) -> Document:
    reader = PdfReader(BytesIO(file_bytes))
    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return ingest_text(business_id, title, text, source_type="pdf")
