"""
文件读取模块
支持TXT、MD、WORD、PDF格式的文件读取
"""
import os
from pathlib import Path
from typing import Optional
import docx
import PyPDF2
from pypdf import PdfReader


class FileReader:
    """文件读取器，支持多种格式"""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.docx', '.doc', '.pdf'}
    
    @staticmethod
    def read_txt(file_path: str) -> str:
        """读取TXT文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
    
    @staticmethod
    def read_md(file_path: str) -> str:
        """读取MD文件"""
        return FileReader.read_txt(file_path)  # MD文件也是文本格式
    
    @staticmethod
    def read_word(file_path: str) -> str:
        """读取WORD文件"""
        try:
            doc = docx.Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            return '\n'.join(paragraphs)
        except Exception as e:
            raise Exception(f"读取Word文件失败: {str(e)}")
    
    @staticmethod
    def read_pdf(file_path: str) -> str:
        """读取PDF文件"""
        try:
            # 使用pypdf库（更现代）
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            # 如果pypdf失败，尝试PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except Exception as e2:
                raise Exception(f"读取PDF文件失败: {str(e2)}")
    
    @classmethod
    def read_file(cls, file_path: str) -> Optional[str]:
        """
        根据文件扩展名自动选择读取方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串，如果文件格式不支持则返回None
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {extension}。支持的格式: {cls.SUPPORTED_EXTENSIONS}")
        
        if extension == '.txt':
            return cls.read_txt(str(file_path))
        elif extension == '.md':
            return cls.read_md(str(file_path))
        elif extension in ['.docx', '.doc']:
            return cls.read_word(str(file_path))
        elif extension == '.pdf':
            return cls.read_pdf(str(file_path))
        else:
            return None
    
    @classmethod
    def read_all_files_in_dir(cls, dir_path: str) -> dict:
        """
        读取目录下所有支持的文件
        
        Args:
            dir_path: 目录路径
            
        Returns:
            字典，key为文件名，value为文件内容
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        files_content = {}
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS:
                try:
                    content = cls.read_file(str(file_path))
                    files_content[file_path.name] = content
                except Exception as e:
                    print(f"读取文件 {file_path.name} 时出错: {str(e)}")
                    continue
        
        return files_content

