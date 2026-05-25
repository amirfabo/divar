import os
import json

class MemorySession:
    """Memory Session Storage"""

    def __init__(self, data: dict | None = None):
        self._data = data.copy() if data else {}

    def load(self) -> dict:
        return self._data.copy()

    def save(self, data: dict) -> bool:
        self._data = data.copy()
        return True

    def exists(self) -> bool:
        return bool(self._data)

class FileSession:
    """File Session Storage"""

    def __init__(self, session_name: str):
        self.session_name = session_name
        self.file_path = os.path.join(
            os.getcwd(),
            f"{session_name}.session"
        )

    def load(self) -> dict:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, cookies: dict) -> bool:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)

        return True

    def exists(self) -> bool:
        return os.path.exists(self.file_path)