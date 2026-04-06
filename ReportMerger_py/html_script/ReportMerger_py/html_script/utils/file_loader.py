from pathlib import Path
from bs4 import BeautifulSoup

class fileloader:

    def __init__(self, directory):
        self.directory = Path(directory)

    def load_files(self):
        files = sorted(f for f in self.directory.glob("*.html") if "MergedReport" not in f.name)

        if not files:
            raise FileNotFoundError(f"No *.html file found in {self.directory}")

        file_soups = []

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                file_soups.append((file, soup))

        return file_soups