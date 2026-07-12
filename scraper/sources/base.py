from abc import ABC, abstractmethod


class BaseSource(ABC):
    name: str = "base"

    @abstractmethod
    def fetch(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw_content: str) -> list[dict]:
        raise NotImplementedError

    def get_items(self) -> list[dict]:
        try:
            raw_content = self.fetch()
            return self.parse(raw_content)
        except Exception as e:
            print(f"❌ Error getting items from {self.name}: {e}")
            return []