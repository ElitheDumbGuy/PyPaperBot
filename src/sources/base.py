from abc import ABC, abstractmethod
from typing import List
from models.paper import Paper

class BaseSource(ABC):
    """Abstract base class for a paper source (Scholar, OpenAlex, etc.)"""
    @abstractmethod
    def search(self, query: str, limit: int) -> List[Paper]:
        pass

