import os
from ja_transliteration_tool.pre_train.editor.ja import EditorJa
from ja_transliteration_tool.pre_train.splitter.ar import SplitterAr
from ja_transliteration_tool.pre_train.splitter.ja import SplitterJa
from ja_transliteration_tool.pre_train.aligner.align import Aligner
from ja_transliteration_tool.pre_train.aligner.frequent_finder import FrequentFinder
from ja_transliteration_tool.pre_train.generic.const import HIDDEN

MAIN_PATH = "../../resources/alkuzari/"
AR_PATH = MAIN_PATH + "ar/"
JA_PATH = MAIN_PATH + "ja/"

RESULTS_PATH = MAIN_PATH + "align/"

coupling_dict = {}
chapters = os.listdir(AR_PATH)
chapters = [int(chapter) for chapter in chapters]
chapters.sort()
for chapter in chapters:
    if os.path.isdir(f"{AR_PATH}/{chapter}") is False:
        continue
    if chapter not in coupling_dict:
        coupling_dict[chapter] = {}
    signs = os.listdir(f"{AR_PATH}/{chapter}")
    signs = [int(sign.split(".")[0]) for sign in signs]
    signs.sort()
    for sign in signs:
        if os.path.isfile(f"{AR_PATH}/{chapter}/{sign}.txt") is False:
            continue

        print(f"start: c {chapter} s {sign}")
        ar_path = f"{AR_PATH}/{chapter}/{sign}.txt"
        ja_path = f"{JA_PATH}/{chapter}/{sign}.txt"

        text_ar = open(ar_path, "r").read()
        text_ja = open(ja_path, "r").read()

        split_ar = SplitterAr(text_ar, keep_punctuation=False).get_split_text()
        edited_ja = EditorJa(ja_path).get_edited_content()
        split_ja = SplitterJa(edited_ja, keep_punctuation=False).get_split_text()

        clear_split_ja = [w for w in split_ja if w != HIDDEN]
        new_split = FrequentFinder(split_ar, clear_split_ja).get_new_text_split()
        coupling_dict[chapter][sign] = []
        for s in new_split:
            coupling_dict[chapter][sign].extend(Aligner(s[0], s[1]).get_tws())

        print(f"stop: c {chapter} s {sign}")

for chapter in coupling_dict:
    if os.path.exists(RESULTS_PATH + str(chapter)) is False:
        os.mkdir(RESULTS_PATH + str(chapter))
    for sign in coupling_dict[chapter]:
        path = f"{RESULTS_PATH}/{str(chapter)}/{str(sign)}.txt"
        with open(path, "w") as f:
            f.write("\n".join([str(tw.couple_letters()) for tw in coupling_dict[chapter][sign]]))

print(1)
