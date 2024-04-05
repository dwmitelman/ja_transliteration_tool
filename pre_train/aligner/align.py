import itertools
from tabulate import tabulate
from typing import List

from ja_transliteration_tool.pre_train.generic.const import *
from ja_transliteration_tool.pre_train.generic.word_clean import Ar, Ja
from ja_transliteration_tool.pre_train.aligner.transliterate import Ja2Ar, Ar2Ja


class Comparator(object):
    def __init__(self, word_ar, word_ja):
        self._word_ar = Ar(word_ar).clean()
        self._word_ja = Ja(word_ja, keep_apostrophe=True).clean()

    def compare(self):
        if self._word_ja == HIDDEN:
            return False, None

        transliterated_to_ja = Ar2Ja(self._word_ar).get_transliterated_words()
        transliterated_to_ar = Ja2Ar(self._word_ja).get_transliterated_words()

        transliterated_candidates = [
            tw
            for tw in transliterated_to_ja
            if tw.ja == self._word_ja
        ] + [
            tw
            for tw in transliterated_to_ar
            if tw.ar == self._word_ar
        ]

        transliterated_candidates.sort(reverse=True)
        # print(transliterated_candidates)
        if len(transliterated_candidates) > 0:
            # print(f"Best option: {transliterated_candidates[0]}")
            return True, transliterated_candidates[0]
        else:
            # print("No option!")
            return False, None


class Aligner(object):
    WORDS_DIST = 10

    def __init__(self, sentence_ar: List[str], sentence_ja: List[str]):
        self._sentence_ar = sentence_ar
        self._sentence_ja = sentence_ja
        self._tws = []

        self._run()

    def _find_couple(self, i_ar: int, i_ja: int, runner_lang: Lang):
        if runner_lang is Lang.AR:
            i_max_ar = i_ar
            i_max_ja = min(len(self._sentence_ja)-1, i_ja + self.WORDS_DIST)
        else:
            i_max_ar = min(len(self._sentence_ar)-1, i_ar + self.WORDS_DIST)
            i_max_ja = i_ja

        for j_ar, j_ja in itertools.product(range(i_ar, i_max_ar+1), range(i_ja, i_max_ja+1)):
            word_ar = self._sentence_ar[j_ar]
            word_ja = self._sentence_ja[j_ja]
            res, tw = Comparator(word_ar, word_ja).compare()
            if res is True:
                tw.i_ar, tw.i_ja = j_ar, j_ja
                return True, tw

        return False, None

    def _parse_sentence(self):
        i_ar, i_ja = 0, 0
        self._tws = []
        while i_ar < len(self._sentence_ar) and i_ja < len(self._sentence_ja):
            is_changed = False
            for runner_lang in Lang:
                res, tw = self._find_couple(i_ar, i_ja, runner_lang)
                if res is True:
                    self._tws.append(tw)
                    i_ar, i_ja = tw.i_ar+1, tw.i_ja+1
                    is_changed = True
                    break
            if is_changed is False:
                print("Could not align")
                i_ar += 1
                i_ja += 1
                # return False

        return True

    def _print_sentence(self):
        sentences = []
        i_last_ar, i_last_ja = -1, -1
        for tw in self._tws:
            for i_ar in range(i_last_ar+1, tw.i_ar):
                sentences.append({"couple": "", Lang.AR.name: self._sentence_ar[i_ar], Lang.JA.name: ""})
            for i_ja in range(i_last_ja+1, tw.i_ja):
                sentences.append({"couple": "", Lang.JA.name: "", Lang.AR.name: self._sentence_ja[i_ja]})
            sentences.append({"couple": str(tw.couple()), Lang.JA.name: "", Lang.AR.name: ""})
            i_last_ar, i_last_ja = tw.i_ar, tw.i_ja

        print(tabulate([[s[k] for k in s.keys()] for s in sentences], tablefmt="pretty", headers=["couples", Lang.AR.name, Lang.JA.name]))

    def _run(self):
        res = self._parse_sentence()
        assert res
        # self._print_sentence()

    def get_tws(self):
        return self._tws
