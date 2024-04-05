from align import Aligner


def sample(text_ar, text_ja):
    split_ar = text_ar.split()
    split_ja = text_ja.split()

    # print(len(split_ja), len(split_ar))
    # assert len(split_ja) == len(split_ar)

    return Aligner(split_ar, split_ja)

    # for i in range(len(split_ar)):
    #     assert Comparator(split_ar[i], split_ja[i]).compare()


text_ar = "سُئِلْتُ عمّا عنديَ من الاحتجاج خخخخخخخ على مُخالفينا من الفلاسفة وأهل الأديان ثمّ على الخوارج الذين يخالفون الجمهور"
text_ja = "סילת עמא ענדי מן אלאחתג'אג' עלי מכ'אלפינא מן <אלפלאספה> ואה<ל אלאדיאן> ת'ם עלי אלכ'וארג עעעעעעעע אלד'ין יכ'אלפון אלג'מהור"

res = sample(text_ar, text_ja).get_tws()
print(res)
