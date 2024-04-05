from math import ceil, floor
from copy import deepcopy
from typing import List, Tuple, Dict
from ja_transliteration_tool.pre_train.aligner.transliterate import Ar2Ja, TW
from ja_transliteration_tool.pre_train.aligner.align import Aligner


class FrequentFinder:
    SUB_MATCH_RANGE = 5
    SUB_MATCH_PCT = 0.75

    def __init__(self, split_ar: List[str], split_ja: List[str]):
        self._split_ar: List[str] = split_ar
        self._split_ja = split_ja

        self._freq_map_ar = self._freq_mapper()
        self._rare_words_map = self._rare_words_mapper()
        self._rare_words_for_match = self._rare_words_finder()
        self._rare_words_matched = self._rare_words_matcher()
        self._rare_words_enricher()
        self._new_split = self._text_splitter()

    def _freq_mapper(self) -> Dict[str, int]:
        freq_map_ar: Dict[str, int] = {}
        for w in self._split_ar:
            if w not in freq_map_ar:
                freq_map_ar[w] = 0
            freq_map_ar[w] += 1

        return freq_map_ar

    def _rare_words_mapper(self) -> Dict[int, List[str]]:
        rare_words = [w for w in self._freq_map_ar if self._freq_map_ar[w] == 1]
        rare_words_map: Dict[int, List[str]] = {}
        for w in rare_words:
            if len(w) not in rare_words_map:
                rare_words_map[len(w)] = []
            rare_words_map[len(w)].append(w)

        return rare_words_map

    def _calc_ev(self) -> float:
        return sum(l * len(self._rare_words_map[l]) for l in self._rare_words_map) / sum(len(self._rare_words_map[l]) for l in self._rare_words_map)

    def _rare_words_finder(self) -> List[str]:
        max_length = max(self._rare_words_map.keys())
        min_length = self._calc_ev()  # floor((self._calc_ev() + max_length) / 2)

        rare_words_for_match: List[str] = []
        for l in self._rare_words_map:
            if not floor(min_length) <= l <= max_length:
                continue
            rare_words_for_match.extend(self._rare_words_map[l])

        return rare_words_for_match

    def _sub_match_idx(self, idx: int, max_idx: int) -> Tuple[int, int]:
        if max_idx < 2 * self.SUB_MATCH_RANGE:
            return 0, max_idx

        if idx < self.SUB_MATCH_RANGE:
            return 0, 2 * self.SUB_MATCH_RANGE

        if idx > max_idx - self.SUB_MATCH_RANGE:
            return max_idx - 2 * self.SUB_MATCH_RANGE, max_idx

        i_min = max(idx - self.SUB_MATCH_RANGE, 0)
        i_max = min(idx + self.SUB_MATCH_RANGE, max_idx)

        return i_min, i_max

    def _sub_match_align(self, tw: TW) -> bool:
        i_min_ar, i_max_ar = self._sub_match_idx(tw.i_ar, len(self._split_ar) - 1)
        i_min_ja, i_max_ja = self._sub_match_idx(tw.i_ja, len(self._split_ja) - 1)

        sub_split_ar, sub_split_ja = self._split_ar[i_min_ar:i_max_ar + 1], self._split_ja[i_min_ja:i_max_ja + 1]
        aligned_result = Aligner(sub_split_ar, sub_split_ja).get_tws()

        return len(aligned_result) / len(sub_split_ar) > self.SUB_MATCH_PCT and len(aligned_result) / len(sub_split_ja) > self.SUB_MATCH_PCT

    @staticmethod
    def _get_word_idx(word: str, split_text: List[str]) -> List[int]:
        return [i for i in range(len(split_text)) if split_text[i] == word]

    def _rare_words_matcher(self) -> List[TW]:
        rare_words_matched: List[TW] = []

        for w_ar in self._rare_words_for_match:
            transliterated_words: List[TW] = Ar2Ja(w_ar).get_transliterated_words()
            transliterated_words = [tw for tw in transliterated_words if tw.has_empty() is False]

            potential_matches: List[TW] = []
            for tw in transliterated_words:
                if tw.ja not in self._split_ja:
                    continue

                tw.i_ar = self._get_word_idx(tw.ar, self._split_ar)[0]
                indices_ja = self._get_word_idx(tw.ja, self._split_ja)
                for idx_ja in indices_ja:
                    curr_tw = deepcopy(tw)
                    curr_tw.i_ja = idx_ja
                    if self._sub_match_align(curr_tw) is False:
                        continue
                    potential_matches.append(curr_tw)

            # if len(potential_matches) == 0:
            #     continue
            # best_score_match = max(tw.score() for tw in potential_matches)
            # best_curr_matches = [tw for tw in potential_matches if tw.score() == best_score_match]

            if len(potential_matches) != 1:
                continue

            rare_words_matched.append(potential_matches[0])

        return rare_words_matched

    @staticmethod
    def _calc_illegal_indices(curr_rare_words_matched):
        indices = [(tw.i_ar, tw.i_ja) for tw in curr_rare_words_matched]
        legal_per_index = [indices[i][1] < indices[i + 1][1] for i in range(len(indices)) if i < len(indices) - 1]
        return [i for i in range(len(legal_per_index)) if legal_per_index[i] is False]

    def _rare_words_enricher(self) -> None:
        # for tw in self._rare_words_matched:
        #     group_ar = [i for i in range(len(self._split_ar)) if self._split_ar[i] == tw.ar]
        #     group_ja = [i for i in range(len(self._split_ja)) if self._split_ja[i] == tw.ja]
        #     if len(group_ar) != 1 or len(group_ja) != 1:
        #         print(1)
        #         assert len(group_ar) != 1 or len(group_ja) != 1
        #     tw.i_ar = group_ar[0]
        #     tw.i_ja = group_ja[0]

        self._rare_words_matched.sort(key=lambda t: t.i_ar)
        self._verify_index()
        print(1)

        # for tw in self._rare_words_matched:
        #     print(self._split_ar[tw.i_ar - 5:tw.i_ar + 5])
        #     print(self._split_ja[tw.i_ja - 5:tw.i_ja + 5])

        # illegal_indices = self._calc_illegal_indices(self._rare_words_matched)

        # for i in range(min(illegal_indices) - 2, max(illegal_indices) + 3):
        #     add = '*' if i in illegal_indices else ''
        #     print(self._rare_words_matched[i].i_ar, self._rare_words_matched[i].i_ja, add)
        #     i_ar = self._rare_words_matched[i].i_ar
        #     i_ja = self._rare_words_matched[i].i_ja
        #     print(self._split_ar[i_ar - 5:i_ar + 5], add)
        #     print(self._split_ja[i_ja - 5:i_ja + 5], add)

        # max_idx = len(self._split_ja)-1
        # for idx in reversed(illegal_indices):
        #     did_truncate = False
        #     for curr_idx in range(max(idx-1, 0), min(idx+1, max_idx)+1):
        #         curr_rare_words = self._rare_words_matched[:curr_idx] + self._rare_words_matched[curr_idx+1:]
        #         curr_illegal_indices = self._calc_illegal_indices(curr_rare_words)
        #         if len(curr_illegal_indices) < len(illegal_indices):
        #             self._rare_words_matched = curr_rare_words
        #             illegal_indices = self._calc_illegal_indices(self._rare_words_matched)
        #             did_truncate = True
        #             break
        #     if did_truncate is False:
        #         print(1)
        #         assert did_truncate is True

    def _verify_index(self) -> None:
        illegal_indices = self._calc_illegal_indices(self._rare_words_matched)
        if len(illegal_indices) != 0:
            print(1)
        assert len(illegal_indices) == 0
        # indices = [(tw.i_ar, tw.i_ja) for tw in self._rare_words_matched]
        #
        # assert all(indices[i][0] < indices[i + 1][0] for i in range(len(indices)) if i < len(indices) - 1)
        # if all(indices[i][1] < indices[i + 1][1] for i in range(len(indices)) if i < len(indices) - 1) is False:
        #     print(1)
        # assert all(indices[i][1] < indices[i + 1][1] for i in range(len(indices)) if i < len(indices) - 1)

    def _text_splitter(self) -> List[List[List[str]]]:
        new_split: List[List[List[str]]] = []

        if len(self._rare_words_matched) == 0:
            return [[self._split_ar, self._split_ja]]

        # First
        new_split.append(
            [
                self._split_ar[:self._rare_words_matched[0].i_ar],
                self._split_ja[:self._rare_words_matched[0].i_ja]
            ]
        )
        # print("len = ", len(self._split_ar[:self._rare_words_matched[0].i_ar]))
        # print(0, self._rare_words_matched[0].i_ar)
        # print("calc = ", self._rare_words_matched[0].i_ar-0)
        # print("***0")

        for i in range(1, len(self._rare_words_matched)):
            new_split.append(
                [
                    self._split_ar[self._rare_words_matched[i - 1].i_ar:self._rare_words_matched[i].i_ar],
                    self._split_ja[self._rare_words_matched[i - 1].i_ja:self._rare_words_matched[i].i_ja]
                ]
            )
            # print("len = ", len(self._split_ar[self._rare_words_matched[i - 1].i_ar:self._rare_words_matched[i].i_ar]))
            # print(self._rare_words_matched[i - 1].i_ar, self._rare_words_matched[i].i_ar)
            # print("calc = ", self._rare_words_matched[i].i_ar - self._rare_words_matched[i - 1].i_ar)
            # print("***1")

        # Last
        new_split.append(
            [
                self._split_ar[self._rare_words_matched[-1].i_ar:],
                self._split_ja[self._rare_words_matched[-1].i_ja:]
            ]
        )
        # print("len = ", len(self._split_ar[self._rare_words_matched[-1].i_ar:]))
        # print(self._rare_words_matched[-1].i_ar, len(self._split_ar))
        # print("calc = ", len(self._split_ar) - self._rare_words_matched[-1].i_ar)
        # print("***2")

        assert sum(len(l[0]) for l in new_split) == len(self._split_ar)
        assert sum(len(l[1]) for l in new_split) == len(self._split_ja)

        return new_split

    def get_new_text_split(self) -> List[List[List[str]]]:
        return self._new_split
