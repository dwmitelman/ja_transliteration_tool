from ar import SplitterAr


text = """
سُئِلْتُ عمّا عنديَ من الاحتجاج على مُخالفينا من الفلاسفة وأهل الأديان ثمّ على الخوارج الذين يخالفون الجمهور. و
"""
split_sentence = SplitterAr(text)._run()
print(split_sentence)
