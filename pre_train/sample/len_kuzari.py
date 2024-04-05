import os
from ja_transliteration_tool.pre_train.editor.ja import EditorJa
from ja_transliteration_tool.pre_train.splitter.ar import SplitterAr
from ja_transliteration_tool.pre_train.splitter.ja import SplitterJa
from ja_transliteration_tool.pre_train.aligner.align import Aligner

MAIN_PATH = "../../resources/alkuzari/"
AR_PATH = MAIN_PATH + "ar/"
JA_PATH = MAIN_PATH + "ja/"

coupling_dict = {}
chapters = os.listdir(AR_PATH)
chapters = [int(chapter) for chapter in chapters]
chapters.sort()

sum_ar, sum_ja = 0, 0
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

        # print(f"start: c {chapter} s {sign}")
        ar_path = f"{AR_PATH}/{chapter}/{sign}.txt"
        ja_path = f"{JA_PATH}/{chapter}/{sign}.txt"

        text_ar = open(ar_path, "r").read()
        text_ja = open(ja_path, "r").read()

        split_ar = SplitterAr(text_ar, keep_punctuation=False).get_split_text()
        edited_ja = EditorJa(ja_path).get_edited_content()
        split_ja = SplitterJa(edited_ja, keep_punctuation=False).get_split_text()

        sum_ar += len(split_ar)
        sum_ja += len([x for x in edited_ja if x[1] == 0])

        # coupling_dict[chapter][sign] = Aligner(split_ar, split_ja).get_tws()
        # print(f"stop: c {chapter} s {sign}")

print(f"AR={sum_ar} JA={sum_ja}")
print(1)
