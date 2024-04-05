import pyarabic.araby as araby
from ja_transliteration_tool.pre_train.generic.word_clean import Ar


class SplitterAr(object):
    AR_LETTERS = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوىي"
    HE_LETTERS = "אבגדהוזחטיךכלםמןנסעףפץצקרשת"
    SPACE = " "
    REPLACEMENT_MAP = {
        'آ': 'ا',
        'إ': 'ا',
        'أ': 'ا'
    }
    # LEGAL_CHARACTERS = "ابتثجحخدذرزسشصضطظعغفقكلمنهويءآأإةؤئى"
    PUNCTUATION = ".,:;"

    def __init__(self, text: str, keep_punctuation=True):
        self._orig_text = self._clear_text(text)
        self._split_text = None
        self._keep_punctuation = keep_punctuation

        self._run()

    def _clear_text(self, text):
        text = ''.join([c for c in text if c in self.AR_LETTERS+self.SPACE+self.PUNCTUATION])
        text = text.translate(str.maketrans(self.REPLACEMENT_MAP))
        return ' '.join(w for w in text.split() if len(w) > 0)

    def _split(self, word: str):
        split_list = []
        sub_word = ""

        for c in word:
            if c in araby.LETTERS:  # or c in araby.TASHKEEL:
                sub_word += c
            else:
                split_list.append(sub_word)
                sub_word = ""
                if self._keep_punctuation and c in self.PUNCTUATION:
                    split_list.append(c)
        split_list.append(sub_word)

        return [sub for sub in split_list if sub]

    @staticmethod
    def _text_to_words(text: str):
        return text.strip().split(" ")

    def _run(self):
        res = []

        words = self._text_to_words(self._orig_text)
        for word in words:
            word = araby.strip_diacritics(word)
            res.extend(self._split(word))

        self._split_text = res

    def get_split_text(self):
        return self._split_text
