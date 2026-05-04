from pathlib import Path
import random


class ProxyManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def add_many(self, text: str) -> int:
        lines = [x.strip() for x in text.splitlines()
                 if x.strip() and not x.strip().startswith('#')]
        if not lines:
            return 0
        with self.path.open('a', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
        return len(lines)

    def all(self):
        return [
            x.strip() for x in self.path.read_text(encoding='utf-8').splitlines()
            if x.strip() and not x.strip().startswith('#')
        ]

    def choose(self):
        items = self.all()
        return random.choice(items) if items else None

    def remove(self, proxy: str):
        items = [x for x in self.all() if x != proxy]
        self.path.write_text(
            '\n'.join(items) + ('\n' if items else ''),
            encoding='utf-8'
        )
