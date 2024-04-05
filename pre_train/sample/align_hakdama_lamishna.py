import os
from ja_transliteration_tool.pre_train.editor.ja import EditorJa
from ja_transliteration_tool.pre_train.splitter.ar import SplitterAr
from ja_transliteration_tool.pre_train.splitter.ja import SplitterJa
from ja_transliteration_tool.pre_train.aligner.align import Aligner
from ja_transliteration_tool.pre_train.generic.const import HIDDEN
from ja_transliteration_tool.pre_train.aligner.frequent_finder import FrequentFinder

MAIN_PATH = "../../resources/hakdama lamishna/"
AR_PATH = MAIN_PATH + "ar/"
JA_PATH = MAIN_PATH + "ja/"

RESULTS_PATH = MAIN_PATH + "align/"

# AR_IDX = [
#     0,
#     986,
#     1983,
#     2853,
#     4081,
#     5061,
#     6013,
#     7124,
#     8123,
#     9163,
#     9802,
#     10878
# ]
#
# JA_IDX = [
#     0,
#     991,
#     1954,
#     2778,
#     3966,
#     4874,
#     5794,
#     7260,
#     8463,
#     9672,
#     10327,
#     11402
# ]

# assert len(AR_IDX) == len(JA_IDX)

paths_ar = os.listdir(AR_PATH)
paths_ar.sort()
text_ar = ' '.join([open(f"{AR_PATH}/{path}", "r").read() for path in paths_ar])

ja_path = f"{JA_PATH}/ja_file.csv"

split_ar = SplitterAr(text_ar, keep_punctuation=False).get_split_text()
edited_ja = EditorJa(ja_path).get_edited_content()
split_ja = SplitterJa(edited_ja, keep_punctuation=False).get_split_text()
clear_split_ja = [w for w in split_ja if w != HIDDEN]
new_split = FrequentFinder(split_ar, clear_split_ja).get_new_text_split()

coupling = []
for s in new_split:
    coupling.extend(Aligner(s[0], s[1]).get_tws())

with open(f"{RESULTS_PATH}/align.txt", "w") as f:
    f.write("\n".join([str(tw.couple_letters()) for tw in coupling]))

print(1)


# for i in range(len(AR_IDX)):
#     last_idx_ar = AR_IDX[i + 1] if i < len(AR_IDX) - 1 else len(split_ar)
#     last_idx_ja = JA_IDX[i + 1] if i < len(JA_IDX) - 1 else len(split_ja)
#
#     print("Start coupling round ", i)
#     clear_split_ja = [w for w in split_ja[JA_IDX[i]:last_idx_ja] if w != HIDDEN]
#     coupling.extend(Aligner(split_ar[AR_IDX[i]:last_idx_ar], split_ja[JA_IDX[i]:last_idx_ja]).get_tws())
#     print("Finish coupling round ", i)

#
# for chapter in coupling_dict:
#     if os.path.exists(RESULTS_PATH + str(chapter)) is False:
#         os.mkdir(RESULTS_PATH + str(chapter))
#     for sign in coupling_dict[chapter]:
#         path = f"{RESULTS_PATH}/{str(chapter)}/{str(sign)}.txt"
#         with open(path, "w") as f:
#             f.write("\n".join([str(tw.couple_letters()) for tw in coupling_dict[chapter][sign]]))
