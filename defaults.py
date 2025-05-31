from typing import Callable, Dict, List
import eng_to_ipa
from nltk.corpus import wordnet

def english_defaults(word: str) -> List[Dict[str, str]]:
    """Return a list of default options (definition, IPA, example) for each WordNet synset."""
    synsets = wordnet.synsets(word, lang='eng')
    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = "/" + "; ".join(ipa_list) + "/"
    options: List[Dict[str, str]] = []
    for syn in synsets:
        definition = syn.definition() or ""
        examples_list = syn.examples() or []
        example = "; ".join(examples_list)
        options.append({"definition": definition, "ipa": ipa, "example": example})
    if not options:
        options.append({"definition": "", "ipa": ipa, "example": ""})
    return options

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, str]]]] = {
    "English": english_defaults,
}
