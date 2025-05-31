from typing import Callable, Dict, List, Any
import eng_to_ipa
from nltk.corpus import wordnet

def english_defaults(word: str) -> List[Dict[str, Any]]:
    """Return a list of default options (definition, IPA, examples, POS, synonyms) for each WordNet synset."""
    synsets = wordnet.synsets(word, lang='eng')
    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = "/" + "; ".join(ipa_list) + "/"
    options: List[Dict[str, Any]] = []
    pos_map = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}
    for syn in synsets:
        definition = syn.definition() or ""
        examples_list = syn.examples() or []
        raw_pos = syn.pos()
        pos = pos_map[raw_pos]
        lemmas = [lemma.name().replace("_", " ") for lemma in syn.lemmas()]
        synonyms = "; ".join([l for l in lemmas if l.lower() != word.lower()])
        options.append({
            "definition": definition,
            "ipa": ipa,
            "examples": examples_list,
            "pos": pos,
            "function": pos,
            "synonyms": synonyms,
        })
    if not options:
        options.append({
            "definition": "",
            "ipa": ipa,
            "examples": [],
            "pos": "",
            "function": "",
            "synonyms": "",
        })
    return options

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
    "English": english_defaults,
}
