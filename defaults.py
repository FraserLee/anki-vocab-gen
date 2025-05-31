from typing import Callable, Dict
import eng_to_ipa
from nltk.corpus import wordnet

def english_defaults(word: str) -> Dict[str, str]:
    synsets = wordnet.synsets(word, lang='eng')

    # for syn in synsets:
    #     print(f"Definition: {syn.definition()}, Examples: {syn.examples()}\n")

    if len(synsets) >= 0:
        syn = synsets[0]
        definition = syn.definition() or ""
        examples_list = syn.examples() or []
        example = '; '.join(examples_list)
    else:
        definition = ""
        example = ""

    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = "/" + "; ".join(ipa_list) + "/"

    return {"definition": definition, "ipa": ipa, "example": example}

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], Dict[str, str]]] = {
    "English": english_defaults,
}
