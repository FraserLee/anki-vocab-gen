from typing import Callable, Dict, List, Any
import re
import eng_to_ipa
from nltk.corpus import wordnet
from pypinyin import pinyin, Style

POS_MAP = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}

def get_syn_options(word: str, lang: str) -> List[Dict[str, Any]]:
    options: List[Dict[str, Any]] = []
    synsets = wordnet.synsets(word, lang=lang)
    for syn in synsets:
        definition = syn.definition() or ""
        examples_list = syn.examples() or []
        # bold occurrences of the term in each example sentence
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        examples_list = [pattern.sub(lambda m: f"<b>{m.group(0)}</b>", ex)
                         for ex in examples_list]
        pos = POS_MAP[syn.pos()]
        lemmas = [lemma.name().replace("_", " ") for lemma in syn.lemmas()]
        synonyms = "; ".join([l for l in lemmas if l.lower() != word.lower()])
        options.append({
            "definition": definition,
            "example": examples_list,
            "pos": pos,
            "function": pos,
            "synonyms": synonyms,
        })

    return options


def english_defaults(word: str) -> List[Dict[str, Any]]:

    ipa_list = eng_to_ipa.convert(word, retrieve_all=True)
    ipa = "/" + "; ".join(ipa_list) + "/"

    options: List[Dict[str, Any]] = []

    for option in get_syn_options(word, lang='eng'):
        option["ipa"] = ipa
        options.append(option)
    if not options:
        options.append({})

    return options

def chinese_defaults(word: str) -> List[Dict[str, Any]]:
    pinyin_list = pinyin(word, style=Style.TONE, heteronym=False)
    pinyin_str = " ".join(syll[0] for syll in pinyin_list)
    options: List[Dict[str, Any]] = []
    for option in get_syn_options(word, lang='cmn'):
        option["pinyin"] = pinyin_str
        options.append(option)
    if not options:
        options.append({})
    return options

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
    "English": english_defaults,
    "Chinese": chinese_defaults,
}
