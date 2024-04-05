from ja_transliteration_tool.pre_train.generic.const import *


class SplitterJa(object):
    LEGAL_CHARACTERS = "אבגדהוזחטיכלמנסעפצקרשתךםןףץ"
    PUNCTUATION = ".,:;׳'"

    def __init__(self, text: (str, int), keep_punctuation=False):
        self._orig_text = text
        self._split_text = None
        self._keep_punctuation = keep_punctuation

        self._run()

    def _run(self):
        res = []

        for word, lang in self._orig_text:
            if lang == 0:
                res.append(word)
            elif lang == 1:
                res.append(HIDDEN)
            elif lang == 2 and self._keep_punctuation:
                res.append(word)

        self._split_text = res

    def get_split_text(self):
        return self._split_text
