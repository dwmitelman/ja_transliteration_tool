import pandas as pd


class EditorJa(object):
    HEB = "אבגדהוזחטיכלמנסעפצקרשתךםןףץ"
    LEGAL = """׳אבגדהוז"חטיכלמנסעפצקרשתךםןףץ""" + """הֿ"""
    PUNCTUATION_SET = ".,:;"

    PUNCTUATION = 2
    HEBREW = 1
    NON_HEBREW = 0

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._file_content = []
        self._edited_content = None

        self._run()

    def _has_hebrew_letters(self, word):
        return any([c in self.HEB for c in word])

    @staticmethod
    def _get_file_content(file_path):
        with open(file_path, 'rb') as f:
            article_content_str = f.read()
            return eval(article_content_str)

    @staticmethod
    def _get_csv_content(file_path):
        df = pd.read_csv(file_path)
        return [(df["word"][i], df["is_he"][i]) for i in range(len(df))]

    def save_file_content(self, file_path):
        with open(file_path, 'w') as f:
            f.write(str(self._file_content))

    def _split_punctuation(self, word, language):
        if word[-1] in self.PUNCTUATION_SET:
            return [(word[:-1], language), (word[-1], self.PUNCTUATION)]
        else:
            return [(word, language)]

    def _remove_irrelevant_characters(self, word, language):
        word = word.translate(str.maketrans("'", "׳"))
        new_word = "".join([c for c in word if c in self.LEGAL])

        if word != new_word:
            print(f"word={word} new_word={new_word}")

        return new_word, language

    def _edit_content(self, content):
        edited_content = []
        for word, language in content:
            if not self._has_hebrew_letters(word):
                continue
            words = self._split_punctuation(word, language)
            words[0] = self._remove_irrelevant_characters(words[0][0], words[0][1])
            edited_content.extend(words)

        return edited_content

    def _run(self):
        self._file_content = self._get_file_content(self._file_path) if self._file_path.endswith(".txt") else self._get_csv_content(self._file_path)
        self._edited_content = self._edit_content(self._file_content)

    def get_edited_content(self):
        return self._edited_content
