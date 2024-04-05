import os
import pandas as pd

MAIN_PATH = "../../resources/alkuzari/"
ALIGN_LISTS_PATH = MAIN_PATH + "align/"

chapters = os.listdir(ALIGN_LISTS_PATH)
chapters = [int(chapter) for chapter in chapters]
chapters.sort()

for chapter in chapters:
    if os.path.isdir(f"{ALIGN_LISTS_PATH}/{chapter}") is False:
        continue
    signs = os.listdir(f"{ALIGN_LISTS_PATH}/{chapter}")
    signs = [int(sign.split(".")[0]) for sign in signs]
    signs.sort()
    for sign in signs:
        if os.path.isfile(f"{ALIGN_LISTS_PATH}/{chapter}/{sign}.txt") is False:
            continue

        # print(f"start: c {chapter} s {sign}")
        path = f"{ALIGN_LISTS_PATH}/{chapter}/{sign}.txt"
        text = open(path, "r").read().split('\n')
        for line in text:
            for couple in eval(line):
                l_ar, l_ja = couple
                if not l_ar:
                    print(f"JA: {''.join([c[1] for c in eval(line)])} -> (AR): {''.join([c[0] for c in eval(line)])}")
                    break
                if not l_ja:
                    print(f"(JA): {''.join([c[1] for c in eval(line)])} -> AR: {''.join([c[0] for c in eval(line)])}")
                    break

print(1)
