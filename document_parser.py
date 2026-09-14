import io
import re
import base64
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Union, Tuple

class DocumentParser:
    """Parses various document formats (PDF, DOCX, TXT) into cleaned text for LLM analysis, 
    with native support for scanned PDFs via Gemini Multimodal."""

    @staticmethod
    def extract_text_from_pdf(file_bytes_or_path: Union[bytes, str]) -> Tuple[str, bool, str]:
        """Extracts text from PDF using PyMuPDF (fitz) and detects if PDF is scanned."""
        try:
            import fitz
            if isinstance(file_bytes_or_path, bytes):
                doc = fitz.open(stream=file_bytes_or_path, filetype="pdf")
                raw_bytes = file_bytes_or_path
            else:
                doc = fitz.open(file_bytes_or_path)
                with open(file_bytes_or_path, "rb") as f:
                    raw_bytes = f.read()

            pages_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    pages_text.append(f"--- [Sahifa {page_num + 1}] ---\n{text}")

            full_text = "\n\n".join(pages_text)
            word_count = len(full_text.split())
            # If multi-page document has very few words (< 25 words), it is likely a scanned PDF
            is_scanned = (len(doc) > 0 and word_count < 25)
            b64_pdf = base64.b64encode(raw_bytes).decode("utf-8") if len(raw_bytes) < 18 * 1024 * 1024 else ""

            return full_text, is_scanned, b64_pdf
        except Exception as e:
            return f"PDF o'qishda xatolik: {str(e)}", False, ""

    @staticmethod
    def extract_text_from_docx(file_bytes_or_path: Union[bytes, str]) -> str:
        """Extracts text from Word DOCX using zero-dependency zipfile + XML parser."""
        try:
            if isinstance(file_bytes_or_path, bytes):
                source = io.BytesIO(file_bytes_or_path)
            else:
                source = file_bytes_or_path

            with zipfile.ZipFile(source) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = []
                for p in tree.iterfind(".//w:p", namespaces):
                    texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
                    if texts:
                        paragraphs.append("".join(texts))
                return "\n".join(paragraphs)
        except Exception as e:
            return f"DOCX o'qishda xatolik: {str(e)}"

    @classmethod
    def parse_document(cls, filename: str, file_content: Union[bytes, str]) -> Dict[str, Any]:
        """Auto-detects document format and returns structured content with metadata."""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        raw_text = ""
        is_scanned = False
        pdf_base64 = ""

        if ext == "pdf":
            raw_text, is_scanned, pdf_base64 = cls.extract_text_from_pdf(file_content)
            if is_scanned:
                raw_text = (
                    f"DIQQAT: Ushbu PDF hujjat skanerlangan (rasmli) formatda.\n"
                    f"Fayl nomi: {filename}\n"
                    f"AI tahlili bevosita Gemini Multimodal / Vision orqali amalga oshiriladi."
                )
        elif ext in ["docx", "doc"]:
            raw_text = cls.extract_text_from_docx(file_content)
        elif isinstance(file_content, bytes):
            try:
                raw_text = file_content.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = file_content.decode("cp1251", errors="ignore")
        else:
            raw_text = str(file_content)

        cleaned_text = cls.clean_text(raw_text)
        words = len(cleaned_text.split())

        return {
            "filename": filename,
            "extension": ext,
            "word_count": words,
            "text": cleaned_text,
            "is_scanned": is_scanned,
            "pdf_base64": pdf_base64,
            "preview": cleaned_text[:1000] + ("..." if len(cleaned_text) > 1000 else "")
        }

    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans redundant whitespace and normalizes text."""
        # Replace non-breaking spaces
        text = text.replace("\xa0", " ")
        # Remove consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove trailing spaces
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()
