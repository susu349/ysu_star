"""
文档处理模块 - 解析PDF/Markdown/TXT等文件，进行文本分块
"""
import os
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

from ..config import get_settings

settings = get_settings()


@dataclass
class DocumentChunk:
    """文档分块"""
    content: str
    index: int
    metadata: Dict[str, Any] = None
    chunk_type: str = "text"


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str) -> Tuple[str, List[DocumentChunk]]:
        """处理文件，返回完整文本和分块列表"""
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in [".md", ".markdown"]:
            text = self._extract_markdown(file_path)
        elif ext in [".txt", ".text"]:
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        chunks = self.split_text(text)
        return text, chunks

    def _extract_pdf(self, file_path: str) -> str:
        """提取PDF文本"""
        if not HAS_PDF:
            raise ImportError("需要安装 PyPDF2: pip install PyPDF2")

        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)

    def _extract_markdown(self, file_path: str) -> str:
        """提取Markdown文本（先转HTML再提取纯文本）"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if HAS_MARKDOWN:
            # 简单处理：移除Markdown标记
            import re
            # 移除标题标记
            content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)
            # 移除粗体斜体
            content = re.sub(r"\*\*(.*?)\*\*", r"\1", content)
            content = re.sub(r"\*(.*?)\*", r"\1", content)
            # 移除链接
            content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)

        return content

    def _extract_text(self, file_path: str) -> str:
        """提取纯文本"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def split_text(self, text: str) -> List[DocumentChunk]:
        """
        智能文本分块
        优先按段落分割，其次按句子，最后强制分割
        """
        chunks = []

        # 先按段落分割
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        current_chunk = ""
        current_index = 0

        for para in paragraphs:
            # 如果当前段落就超过chunk_size，需要在段落内分割
            if len(para) > self.chunk_size:
                # 先把之前的保存
                if current_chunk:
                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        index=current_index,
                        chunk_type="text"
                    ))
                    current_index += 1
                    current_chunk = ""

                # 分割长段落
                sentences = self._split_sentences(para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) > self.chunk_size and current_chunk:
                        chunks.append(DocumentChunk(
                            content=current_chunk.strip(),
                            index=current_index,
                            chunk_type="text"
                        ))
                        current_index += 1
                        # 保留重叠
                        overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                        current_chunk = current_chunk[overlap_start:] + " " + sent
                    else:
                        current_chunk += " " + sent if current_chunk else sent

            elif len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                # 保存当前chunk
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    index=current_index,
                    chunk_type="text"
                ))
                current_index += 1
                # 保留重叠
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # 保存最后一个chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                index=current_index,
                chunk_type="text"
            ))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """按句子分割"""
        # 简单实现，中文按句号、问号、感叹号分割
        import re
        sentences = re.split(r'([。！？.!?])', text)
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if sentences[i]:
                result.append(sentences[i] + sentences[i + 1])
        if len(sentences) % 2 == 1 and sentences[-1]:
            result.append(sentences[-1])
        return result


def content_hash(content: str) -> str:
    """计算内容哈希"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
