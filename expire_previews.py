"""Remove expired Contatto snapshots and leave local project files untouched."""
import json
from pathlib import Path
import re
import shutil
import time


def expire(root, now=None):
    root = Path(root).resolve()
    registry_path = root / 'previews.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    now = time.time() if now is None else now
    for key, record in registry.items():
        if not re.fullmatch(r'[a-f0-9]{32}', key):
            raise ValueError('Invalid preview identifier')
        if not isinstance(record.get('expires_at'), (int, float)):
            raise ValueError('Invalid preview expiry')
    expired = [key for key, record in registry.items() if record['expires_at'] <= now]
    for key in expired:
        directory = root / 'public' / 'p' / key
        if directory.is_symlink():
            raise ValueError('Unexpected symbolic link')
        if directory.exists():
            shutil.rmtree(directory)
        del registry[key]
    if expired:
        registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
    return len(expired)


if __name__ == '__main__':
    print(expire(Path(__file__).resolve().parent))
