"""Database adapters for multi-database support"""
from .base import DatabaseAdapter
from .factory import get_database_adapter

__all__ = ['DatabaseAdapter', 'get_database_adapter']
