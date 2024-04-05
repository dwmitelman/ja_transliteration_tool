# Judeo Arabic: Transliteration tool
## [Read our paper!](https://aclanthology.org/2024.findings-eacl.102/)

### Manual

In order to use this tool, we would suggest you running the following commands. It is highly recommended to use a simple environment, such as Google Colab.

### Cloning Code (run only once)
```
%%capture
#@title Cloning Code (run only once)
%cd /content
!if [ -d ja_transliteration_tool ]; then rm -rf ja_transliteration_tool; fi
!git clone https://github.com/dwmitelman/ja_transliteration_tool.git
%cd ja_transliteration_tool
```

### Env Preparation (run only once)
```
%%capture
#@title Env Preparation  (run only once)
!pip install -r global_def/requirements.txt
!huggingface-cli login --token <submit_here_your_hf_token>
```

### Relevant imports (run only once)
```
#@title Relevant imports (run only once)
from run.e2e_pipe import Import, PipelineManager
```

### Input

Please use only one of the following options, and the rest should be commented out (by #):

1. by_list_str: A list of strings, while each string is up to 510 chars. Please use text variable that will make it easier.
2. by_str: Just one string.
3. by_docx_path: Please create a Google Doc file, where every line is a sentence up to 510 chars. Please share this file, and make sure that it is readable for everyone that has the link.

```
initial_input = Import()

text = [
    "והד̇א יוג̇ב אלאסתכ̇ראג̇ אלד̇י לא גני ענה פי אלפראיץ̇ ואלאחכאם",
    "ומא כאן בין אלאמה כ̇לאף פיה אצלא והם קאלו בקל",
    "וחמר וגזרה שוה וכאנו יתנאט̇רון ויחתג̇ אלואחד",
    "עלי צאחבה בחג̇ה מן אלקיאס ויקבלהא ויחתג̇ הד̇א",
    "עלי הד̇א באלאחרי ואלאג̇דר ולא ינכרה ופי קול"
]

str_text = " ".join("""
ראובן הד'א אלמזבח והו קולהם לא לעולה
ולא לזבח כי עד ה' ביננו וביניכם. וקאלו
מחר יאמרו בניכם לבנינו לאמר מה לכם
ולה' אלהי ישראל כלומר מה לכם להקריב
קרבנות על מזבחו ונכרים אתם. חלילה לנו
ממנו למרוד בה', תקדירה חלילה לנו וחוץ
ממנו למרוד בה', אי חאשאנא נחן ען ד'לך,
בל אלכ'ארג ענא הו ג'ירנא יפעלה. אז
""".split("\n"))

link = "https://docs.google.com/document/d/19DXvJpUDb5OT8Sj_KnhwUZXbtdlCne4CNMHMhOja6Lw/edit?usp=sharing"


# initial_input.by_list_str(text)
initial_input.by_str(str_text)
# initial_input.by_docx_path(link)
```

### Converting the JA to AR
```
%%capture
#@title Converting the JA to AR

# output_format = "by_list_str"
output_format = "by_docx_path"
pm = PipelineManager(initial_input.output(), output_format=output_format)
```


### Results
```
if output_format == "by_list_str":
    print("Your transliteration is ready! Here are the results:")
    for sentence in pm.output():
        print("JA input: ")
        print(sentence[0])
        print("Transliterated output: ")
        print(sentence[1])
        print()

elif output_format == "by_docx_path":
    print(f"Your transliteration is ready! Please visit: {pm.output()}")
```