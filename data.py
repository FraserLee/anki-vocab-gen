import os
import nltk
def init() -> None:
    data_dir = os.path.expanduser('~/.anki_card_gen')
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.exists(os.path.join(data_dir, 'corpora' + os.sep + 'wordnet.zip')):
        nltk.download('wordnet', download_dir=data_dir)

