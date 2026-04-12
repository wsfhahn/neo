from rich import print
from pathlib import Path


test_path = Path("test.json")
print([d for d in dir(test_path) if d[0] != "_"])
print(test_path.suffix)
print(test_path.stem)