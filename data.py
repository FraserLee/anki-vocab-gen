import os
import nltk
def init() -> None:
    data_dir = os.path.expanduser('~/.anki_card_gen')
    os.makedirs(data_dir, exist_ok=True)
    nltk.data.path.insert(0, data_dir)

    nltk.download('wordnet', download_dir=data_dir)
    nltk.download('omw-1.4', download_dir=data_dir)

