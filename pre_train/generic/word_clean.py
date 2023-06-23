import pyarabic.araby as araby

from ja_transliteration_tool.pre_train.generic.const import *


class WordClean(object):
    def __init__(self, lang: Lang, legal_characters: str, word: str):
        self._lang = lang
        self._legal_characters = legal_characters
        self._word = word

        self._run()

    def _pre_clean_word(self):
        raise NotImplemented

    def _clean(self):
        self._pre_clean_word()
        illegal_characters = [c for c in self._word if c not in self._legal_characters]
        if illegal_characters:
            print(f"Illegal characters in {self._lang} word {self._word}: {illegal_characters}")

        self._word = ''.join([c for c in self._word if c in self._legal_characters])

    def _run(self):
        self._clean()

    def clean(self):
        return self._word


class Ar(WordClean):
    CHARACTERS = "ابتثجحخدذرزسشصضطظعغفقكلمنهويءةؤئى"  # "آأإ"

    def __init__(self, word):
        super().__init__(Lang.AR, self.CHARACTERS, word)

    def _pre_clean_word(self):
        self._word = araby.strip_diacritics(self._word).translate(str.maketrans("آأإ", "ااا"))


class Ja(WordClean):
    CHARACTERS = "אבגדהוזחטיכלמנסעפצקרשתךםןףץ"

    def __init__(self, word, keep_apostrophe=False):
        self._keep_apostrophe = keep_apostrophe
        _legal_characters = self.CHARACTERS + ("׳" if keep_apostrophe else "")
        super().__init__(Lang.JA, _legal_characters, word)

    def _pre_clean_word(self):
        self._word = self._word.replace("'", "׳")  # To Hebrew version of apostrophe
        self._word = self._word.replace("הֿ", "ה׳")
        if self._keep_apostrophe is False:
            self._word = self._word.replace("׳", "")
