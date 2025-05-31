from typing import Callable, Dict
import eng_to_ipa

def english_defaults(word: str) -> Dict[str, str]:

    definition = "TODO"

    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = '/' + '; '.join(ipa_list) + '/'

    example = "TODO"

    return {"definition": definition, "ipa": ipa, "example": example}

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], Dict[str, str]]] = {
    "English": english_defaults,
}
