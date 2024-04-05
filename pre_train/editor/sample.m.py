import os
from ja import EditorJa

MAIN_PATH = "./../../resources/alkuzari/ja/"

for chapter in os.listdir(MAIN_PATH):
    if os.path.isdir(MAIN_PATH + chapter) is False:
        continue
    for text_file in os.listdir(f"{MAIN_PATH}/{chapter}/", ):
        curr_file = f"{MAIN_PATH}/{chapter}/{text_file}"
        if (os.path.isfile(curr_file) and curr_file.endswith(".txt")) is False:
            continue
        article_content = EditorJa(curr_file).get_edited_content()
        print(1)
