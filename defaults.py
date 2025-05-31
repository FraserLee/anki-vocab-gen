from typing import Callable, Dict, List, Any
import re
import eng_to_ipa
from nltk.corpus import wordnet
from pypinyin import pinyin, Style

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
        # bold occurrences of the term in each example sentence
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        examples_list = [pattern.sub(lambda m: f"<b>{m.group(0)}</b>", ex)
                         for ex in examples_list]
        raw_pos = syn.pos()
        pos = pos_map[raw_pos]
        lemmas = [lemma.name().replace("_", " ") for lemma in syn.lemmas()]
        synonyms = "; ".join([l for l in lemmas if l.lower() != word.lower()])
        options.append({
            "definition": definition,
            "ipa": ipa,
            "example": examples_list,
            "pos": pos,
            "function": pos,
            "synonyms": synonyms,
        })
    if not options:
        options.append({
            "definition": "",
            "ipa": ipa,
            "example": [],
            "pos": "",
            "function": "",
            "synonyms": "",
        })
    return options

def chinese_defaults(word: str) -> List[Dict[str, Any]]:
    """Return a list of default options for a Chinese term using WordNet definitions and auto-generated pinyin."""
    synsets = wordnet.synsets(word, lang="cmn")
    pinyin_list = pinyin(word, style=Style.TONE, heteronym=False)
    pinyin_str = " ".join(syll[0] for syll in pinyin_list)
    pos_map = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}
    options: List[Dict[str, Any]] = []
    for syn in synsets:
        definition = syn.definition() or ""
        raw_pos = syn.pos()
        function = pos_map.get(raw_pos, raw_pos)
        options.append({
            "definition": definition,
            "pinyin": pinyin_str,
            "function": function,
            "example": [],
            "notes": "",
        })
    if not options:
        options.append({
            "definition": "",
            "pinyin": pinyin_str,
            "function": "",
            "example": [],
            "notes": "",
        })
    return options

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
    "English": english_defaults,
    "Chinese": chinese_defaults,
}
