import itertools

from pre_train.generic.const import *
from pre_train.generic.word_clean import Ja


class L(object):
    def __init__(self, l: str, lang: Lang):
        self._l = l
        self._lang = lang

    @property
    def l(self):
        return self._l

    def is_empty(self):
        return len(self._l) == 0

    def score(self):
        raise NotImplemented


class LAR(L):
    def __init__(self, l):
        assert 0 <= len(l) <= 1
        super().__init__(l, Lang.AR)

    def score(self):
        if self.is_empty():
            return 0.01  # Redundant letter in JA
        return 1


class LJA(L):
    def __init__(self, l):
        assert 0 <= len(l) <= 2
        assert not len(l) == 2 or l[1] == APOSTROPHE
        super().__init__(l, Lang.JA)

    def has_apostrophe(self):
        return len(self._l) == 2 and self._l[1] == APOSTROPHE

    def score(self):
        if self.is_empty():
            return 0.1
        if self.has_apostrophe():
            return 2
        return 1


class TL(object):
    # Transliterated Letter
    def __init__(self, letter_ar: str, letter_ja: str):
        self._ar = LAR(letter_ar)
        self._ja = LJA(letter_ja)
        assert not self._ar.is_empty() or not self._ja.is_empty()

    def __repr__(self):
        return f"<ar:{self._ar},ja:{self._ja}"

    @property
    def ar(self):
        return self._ar.l

    @property
    def ja(self):
        return self._ja.l

    def has_empty(self):
        return self._ar.is_empty() or self._ja.is_empty()

    def score(self):
        return self._ar.score() * self._ja.score()


class TW(object):
    # Transliterated Word
    def __init__(self, tls: [TL], trans_from: Lang):
        self._tls = tls
        self._trans_from = trans_from
        self._trans_to = Lang.AR if self._trans_from is Lang.JA else Lang.JA
        self._i_ar, self._i_ja = None, None

    def __repr__(self):
        return f"TW<ar:{self.ar},ja:{self.ja},sc:{self.score()},{self._trans_from.name}2{self._trans_to.name}>"

    def append(self, tl: TL):
        self._tls.append(tl)

    @property
    def ar(self):
        return ''.join([tl.ar for tl in self._tls])

    @property
    def ja(self):
        return ''.join([tl.ja for tl in self._tls])

    def couple(self):
        return self.ar, self.ja

    def couple_letters(self):
        return [(self._tls[i].ar, self._tls[i].ja) for i in range(len(self._tls))]

    @property
    def i_ar(self):
        return self._i_ar

    @property
    def i_ja(self):
        return self._i_ja

    @i_ar.setter
    def i_ar(self, value):
        self._i_ar = value

    @i_ja.setter
    def i_ja(self, value):
        self._i_ja = value

    def score(self):
        decision_factor = 1 if self._trans_from is Lang.AR else 0.5
        return sum([tl.score() for tl in self._tls]) * decision_factor

    def has_empty(self):
        return any(tl.has_empty() for tl in self._tls)

    def __lt__(self, other):
        return self.score() < other.score()

    def __eq__(self, other):
        return self.score() == other.score()


class Transliterate(object):
    def __init__(self, trans_map: dict, trans_from: Lang, word: str):
        self._trans_map = trans_map
        self._trans_from = trans_from
        self._trans_to = Lang.AR if self._trans_from is Lang.JA else Lang.JA
        self._word_from = word
        self._groups_to = []
        self._words_to = []

        self._run()

    def _from_word_to_groups(self):
        for c in self._word_from:
            if c not in self._trans_map:
                print(f"Unknown character in word {self._word_from}: {c}")
                continue

            if self._trans_from is Lang.AR:
                tls = [TL(letter_ar=c, letter_ja=c_to) for c_to in self._trans_map[c]]
            else:
                tls = [TL(letter_ja=c, letter_ar=c_to) for c_to in self._trans_map[c]]
            self._groups_to.append(tls)

    def _from_groups_to_words(self):
        product = list(itertools.product(*self._groups_to))
        self._words_to = [
            TW(p, self._trans_from)
            for p in product
        ]

    def _run(self):
        self._from_word_to_groups()
        self._from_groups_to_words()

    def get_transliterated_words(self):
        return self._words_to


class Ja2Ar(Transliterate):
    JA2AR_MAP = {
        "א": ["ا", "ء", "آ", "أ", "إ", "ئ", "ى", "ؤ", "ٱ", "ه", "ة", ""],
        "ב": ["ب"],
        "ג": ["غ", "ج"],
        "ד": ["ظ", "ض", "ذ", "د"],
        "ה": ["ه", "ة", "ا"],
        "ו": ["ؤ", "و", ""],
        "ז": ["ز", "ظ"],
        "ח": ["ح", "خ"],
        "ט": ["ط", "ظ"],
        "י": ["ي", "ى", "ا", ""],
        "כ": ["خ", "ك"],
        "ל": ["ل"],
        "מ": ["م"],
        "נ": ["ن"],
        "ס": ["س"],
        "ע": ["ع", "غ"],
        "פ": ["ف"],
        "צ": ["ض", "ص"],
        "ק": ["ق"],
        "ר": ["ر"],
        "ש": ["ش"],
        "ת": ["ت", "ث"],
        "ך": ["خ", "ك"],
        "ם": ["م"],
        "ן": ["ن"],
        "ף": ["ف"],
        "ץ": ["ض", "ص"]
    }

    def __init__(self, word: str):
        # JA words will be transliterated w/o an apostrophe
        super().__init__(self.JA2AR_MAP, trans_from=Lang.JA, word=Ja(word, keep_apostrophe=False).clean())


class Ar2Ja(Transliterate):
    AR2JA_MAP = {
        "ا": ["א", ""],
        "ب": ["ב"],
        "ت": ["ת"],
        "ث": ["ת׳", "ת"],
        "ج": ["ג", "ג׳"],
        "ح": ["ח"],
        "خ": ["ח׳", "כ׳", "ך׳", "כ", "ח"],
        "د": ["ד"],
        "ذ": ["ד׳", "ד"],
        "ر": ["ר"],
        "ز": ["ז"],
        "س": ["ס"],
        "ش": ["ש"],
        "ص": ["צ", "ץ"],
        "ض": ["צ׳", "ד", "ץ׳"],
        "ط": ["ט"],
        "ظ": ["ט", "ד", "ז"],
        "ع": ["ע"],
        "غ": ["ג", "ע"],
        "ف": ["פ", "ף"],
        "ق": ["ק"],
        "ك": ["כ", "ך"],
        "ل": ["ל"],
        "م": ["מ", "ם"],
        "ن": ["נ", "ן"],
        "ه": ["ה", ""],
        "و": ["ו", ""],
        "ي": ["י"],
        "ء": ["א", "י", ""],
        "ة": ["ה", "ה׳"],
        "ؤ": ["ו", ""],
        "ئ": ["י", "א", ""],
        "ى": ["א", "י", ""]
    }

    def __init__(self, word: str):
        super().__init__(self.AR2JA_MAP, trans_from=Lang.AR, word=word)
