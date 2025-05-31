from typing import Callable, Dict, List
import eng_to_ipa
from nltk.corpus import wordnet

def english_defaults(word: str) -> List[Dict[str, str]]:
    """Return a list of default options (definition, IPA, example, POS, synonyms) for each WordNet synset."""
    synsets = wordnet.synsets(word, lang='eng')
    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = "/" + "; ".join(ipa_list) + "/"
    options: List[Dict[str, str]] = []
    pos_map = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}
    for syn in synsets:
        definition = syn.definition() or ""
        examples_list = syn.examples() or []
        example = "; ".join(examples_list)
        raw_pos = syn.pos()
        pos = pos_map[raw_pos]
        lemmas = [lemma.name().replace("_", " ") for lemma in syn.lemmas()]
        synonyms = "; ".join([l for l in lemmas if l.lower() != word.lower()])
        options.append({
            "definition": definition,
            "ipa": ipa,
            "example": example,
            "pos": pos,
            "synonyms": synonyms,
        })
    if not options:
        options.append({
            "definition": "",
            "ipa": ipa,
            "example": "",
            "pos": "",
            "synonyms": "",
        })
    return options

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, str]]]] = {
    "English": english_defaults,
}
