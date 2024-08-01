"""
This module provides a unified interface for loading data from various sources.
"""

from data_loader.general_loader import GeneralLoader, PDFLoader, URLLoader, ExcelLoader

__all__ = ['GeneralLoader', 'PDFLoader', 'URLLoader', 'ExcelLoader']
