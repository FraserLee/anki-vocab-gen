import os
import re
import nltk

data_dir = os.path.expanduser('~/.anki_card_gen')
images_dir = os.path.join(data_dir, 'images')

def init() -> None:
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    nltk.data.path.insert(0, data_dir)

    nltk.download('wordnet', download_dir=data_dir)
    nltk.download('omw-1.4', download_dir=data_dir)

def get_new_image_path(word: str, extension: str) -> str:
    sanitised_word = re.sub(r'[<>:"/\\|?*\s]', '_', word)
    i = 0
    potential_path = os.path.join(images_dir, f"{sanitised_word}.{extension}")
    while os.path.exists(potential_path):
        i += 1
        potential_path = os.path.join(images_dir, f"{sanitised_word}_{i}.{extension}")
    return potential_path
