from pathlib import Path
from app.common.config import GLOBAL_SETTINGS


for file in Path.iterdir(GLOBAL_SETTINGS.save_dir):
    if file.is_file():
        print("yp")