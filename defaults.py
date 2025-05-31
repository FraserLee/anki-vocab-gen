from dragonmapper.transcriptions import numbered_to_accented
from nltk.corpus import wordnet
from pycccedict.cccedict import CcCedict
from pypinyin import pinyin, Style
from typing import Callable, Dict, List, Any
import eng_to_ipa
import re

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
            "function": pos,
            "synonyms": synonyms,
        })

    return options

# ----------------------------------- ENGLISH ----------------------------------

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

# ----------------------------------- CHINESE ----------------------------------
# TODO: also add traditional Chinese support

cccedict = CcCedict()


# CL:個|个[ge4],項|项[xiang4]
#         ^^^^^      ^^^^^^^^
pinyin_re = re.compile(r'\[([^\]]+)\]')

# CL:個|个[gè],項|项[xiàng]
#    ^^^       ^^^
trad_cl_re = re.compile(r'CL:([^\|]*).\|(.\[[^\]]+\])')

# trad_other_re
# 長沙|长沙[Cháng shā]
# ^^^^^
trad_other_re = re.compile(r' [^\[\]|]+\|([^\[\]|]+\[[^\[\]|]+\])')

def fix_up_zh(defn):

    changed = True
    while changed:
        defn_shift = pinyin_re.sub(lambda m: '[' + numbered_to_accented(m.group(1)) + ']', defn)
        changed = defn_shift != defn
        defn = defn_shift

    changed = True
    while trad_cl_re.search(defn):
        defn_shift = trad_cl_re.sub(lambda m: 'CL:' + m.group(1) + m.group(2), defn)
        changed = defn_shift != defn
        defn = defn_shift

    changed = True
    while trad_other_re.search(defn):
        defn_shift = trad_other_re.sub(lambda m: ' ' + m.group(1), defn)
        changed = defn_shift != defn
        defn = defn_shift

    return defn

def chinese_defaults(word: str) -> List[Dict[str, Any]]:

    entry = cccedict.get_entry(word)
    options: List[Dict[str, Any]] = []

    # no cccedict entry found: use the pinyin of each character (less accurate)
    if entry is None:
        pinyin_list = pinyin(word, style=Style.TONE, heteronym=False)
        pinyin_str = " ".join(syll[0] for syll in pinyin_list)
    else:
        pinyin_str = numbered_to_accented(entry['pinyin'])
        definitions = entry['definitions']
        definitions = '; '.join(map(lambda x: fix_up_zh(x.strip()), definitions))
        options.append({
            "definition": definitions,
            "pinyin": pinyin_str,
        })

    for option in get_syn_options(word, lang='cmn'):
        option["pinyin"] = pinyin_str
        options.append(option)
    if not options:
        options.append({})
    return options

# ------------------------------------------------------------------------------

LANGUAGE_DEFAULTS: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
    "English": english_defaults,
    "Chinese": chinese_defaults,
}
