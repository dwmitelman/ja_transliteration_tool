import os
import pandas as pd

MAIN_PATH = "../../resources/alkuzari/"
ALIGN_LISTS_PATH = MAIN_PATH + "align/"
FREQ_PATH = MAIN_PATH + "freq/"

count_dict = {}
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
                l_ar = couple[0]
                if l_ar and l_ar not in count_dict:
                    count_dict[l_ar] = 0
                if l_ar:
                    count_dict[l_ar] += 1

        total_sum = sum([count_dict[k] for k in count_dict])
        freq_dict = {k: count_dict[k]/total_sum for k in count_dict}

        inv_freq_dict = {k: 1 / freq_dict[k] for k in freq_dict}
        sum_inv_freq_dict = sum([inv_freq_dict[k] for k in inv_freq_dict])
        n_inv_freq_dict = {k: inv_freq_dict[k] / sum_inv_freq_dict for k in inv_freq_dict}

        s = pd.Series(freq_dict, name="freq")
        s.index.name = "letter"
        s.reset_index()
        with open(FREQ_PATH + "freq_dict.csv", "w") as f:
            f.write(s.to_csv())

        s = pd.Series(n_inv_freq_dict, name="inv_freq")
        s.index.name = "letter"
        s.reset_index()
        with open(FREQ_PATH + "inv_freq_dict.csv", "w") as f:
            f.write(s.to_csv())

print(1)
