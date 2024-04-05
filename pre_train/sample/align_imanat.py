import os
import pandas as pd
from ja_transliteration_tool.pre_train.editor.ja import EditorJa
from ja_transliteration_tool.pre_train.splitter.ar import SplitterAr
from ja_transliteration_tool.pre_train.splitter.ja import SplitterJa
from ja_transliteration_tool.pre_train.aligner.align import Aligner
from ja_transliteration_tool.pre_train.aligner.frequent_finder import FrequentFinder
from ja_transliteration_tool.pre_train.generic.const import HIDDEN

MAIN_PATH = "../../resources/imanat/"
AR_PATH = MAIN_PATH + "ar/"
JA_PATH = MAIN_PATH + "ja/"
RESULTS_PATH = MAIN_PATH + "align/"
FILE_NAME = "ja_file.csv"
coupling_dict = {}

for article in range(1, 11+1):
    coupling_dict[article] = []
    full_article_name = [d for d in os.listdir(JA_PATH) if d.startswith(f"{article} ")][0]
    chapters = os.listdir(f"{JA_PATH}/{full_article_name}")
    chapter_split_ja = []
    for i_chapter in range(len(chapters)):
        curr_full_chapter_name = [d for d in chapters if d.startswith(f"{i_chapter+1} ")][0]
        curr_full_file_path = f"{JA_PATH}/{full_article_name}/{curr_full_chapter_name}/{FILE_NAME}"
        edited_ja = EditorJa(curr_full_file_path).get_edited_content()
        chapter_split_ja.extend(SplitterJa(edited_ja, keep_punctuation=False).get_split_text())

    text_ar = open(f"{AR_PATH}/{article}.txt", "r").read()
    split_ar = SplitterAr(text_ar, keep_punctuation=False).get_split_text()
    clear_split_ja = [w for w in chapter_split_ja if w != HIDDEN]

    new_split = FrequentFinder(split_ar, clear_split_ja).get_new_text_split()
    for s in new_split:
        coupling_dict[article].extend(Aligner(s[0], s[1]).get_tws())

for chapter in coupling_dict:
    if os.path.exists(RESULTS_PATH + str(chapter)) is False:
        os.mkdir(RESULTS_PATH + str(chapter))
    path = f"{RESULTS_PATH}/{str(chapter)}.txt"
    with open(path, "w") as f:
        f.write("\n".join([str(tw.couple_letters()) for tw in coupling_dict[chapter]]))

print(1)
