from typing import Dict, Any, List
from uuid import UUID

class MemoryDB:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

db = MemoryDB()
