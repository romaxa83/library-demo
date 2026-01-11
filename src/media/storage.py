import aiofiles
import os
from abc import ABC, abstractmethod
from pathlib import Path
from fastapi import UploadFile


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, file_content: bytes, destination: str) -> str: pass

    @abstractmethod
    async def delete(self, path: str) -> None: pass


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: Path):
        self.base_path = base_path

    async def save(self, file_content: bytes, destination: str) -> str:
        full_path = self.base_path / destination
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, mode='wb') as f:
            await f.write(file_content)
        return str(destination)

    async def delete(self, path: str) -> None:
        full_path = self.base_path / path
        if full_path.exists():
            os.remove(full_path)