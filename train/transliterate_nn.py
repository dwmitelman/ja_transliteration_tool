import os
from transformers import AutoTokenizer, DataCollatorForTokenClassification, AutoModelForTokenClassification, TrainingArguments, Trainer, AutoConfig
import datasets
import pandas as pd
import evaluate
from datasets import Features, ClassLabel, Value, Sequence
import numpy as np
from datetime import datetime
import sklearn

RESOURCES_PATH = "../../ja_transliteration_tool/resources/align"

AR_LETTERS = "ابتثجحخدذرزسشصضطظعغفقكلمنهويءةؤئى"
EPSILON = "o"
RARE_LETTERS = "تثجخدذصضطظغكءؤئى"

TOKENS = AR_LETTERS + EPSILON

id_to_label = {i: f"B-{TOKENS[i]}" for i in range(len(TOKENS))}
label_to_id = {f"{id_to_label[i]}": i for i in range(len(id_to_label))}

def get_all_couples(subdir: str):
    coupling = []
    for root, dirs, files in os.walk(RESOURCES_PATH + "/" + subdir):
        for file_name in files:
            if file_name.endswith(".txt") is False:
                continue
            with open(f"{root}/{file_name}", "r") as f:
                lines = f.read().split('\n')
                coupling.extend([eval(line) for line in lines])
            # print(f"{root}/{file_name}")

    return coupling


def clear_apostrophe(l, keep_apostrophe: bool):
    assert len(l) <= 2
    if len(l) == 2 and keep_apostrophe is False:
        return l[0]

    return l


def create_words_from_couple(couple: [(str, str)], keep_apostrophe: bool) -> (str, str):
    w_ar, w_ja = "", ""

    for i in range(len(couple)):
        l_ar, l_ja = couple[i][0], clear_apostrophe(couple[i][1], keep_apostrophe)

        if not l_ja:
            continue

        w_ar += l_ar if l_ar else EPSILON
        w_ja += l_ja

    assert len(w_ar) == len(w_ja)

    return w_ar, w_ja


def make_words_list(coupling, keep_apostrophe=False):
    words = []
    for couple in coupling:
        w_ar, w_ja = create_words_from_couple(couple, keep_apostrophe)
        words.append((w_ar, w_ja))

    return words


def split_into_subgroups(words, g_size=20):
    # groups_ar, groups_ja = [], []
    groups = []

    g_ar = [w_ar for w_ar, w_ja in words]
    g_ja = [w_ja for w_ar, w_ja in words]
    groups.extend([[g_ar[i:i + g_size], g_ja[i:i + g_size]] for i in range(0, len(g_ar), g_size)])
    # groups_ja.extend([ for i in range(0, len(g_ja), g_size)])

    for i in range(len(groups)):
        groups[i][0] = [f"B-{l}" for w in groups[i][0] for l in w]

    return groups


tokenizer = AutoTokenizer.from_pretrained("dwmit/transliterate")


def tokenize_and_align_labels(dataset):
    tokenized_inputs = tokenizer(dataset["text"], is_split_into_words=True, truncation=True, max_length=510, padding='max_length')

    labels = []
    for i, label in enumerate(dataset["tag"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = []
        for j, word_idx in enumerate(word_ids):  # Set the special tokens to -100.
            # print(f"j={j}, label={label}, len(label)={len(label)}, word_ids[j]={word_ids[j]}, text={dataset['text'][i]}")
            word_idx = word_ids[j]
            if word_idx is None:
                label_ids.append(-100)
            else:
                label_ids.append(label[j-1])
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels

    return tokenized_inputs


def make_tokenized_datasets(groups, should_split=True):
    df = pd.DataFrame(groups, columns=['tag', 'text'])
    features = Features({
        'text': Sequence(feature=Value(dtype='string', id=None), length=-1),
        'tag': Sequence(feature=ClassLabel(num_classes=34, names=list(label_to_id.keys())), length=-1)
    })
    ds1 = datasets.Dataset.from_pandas(df, features=features)
    ds2 = ds1.map(tokenize_and_align_labels, batched=True)
    columns_to_return = ['input_ids', 'labels', 'attention_mask']
    ds2.set_format(type='torch', columns=columns_to_return)
    ds2 = ds2.remove_columns(['tag', 'text'])
    return ds2.train_test_split(test_size=0.2) if should_split else ds2


def compute_metrics(p):
    predictions, labels, inputs = p
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [id_to_label[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [id_to_label[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    input_tokens = [[tokenizer.decode(t) for t in curr_input if len(tokenizer.decode(t)) == 1 or (len(tokenizer.decode(t)) == 3) and "##" == tokenizer.decode(t)[0:2]] for curr_input in inputs]
    new_letters_idx = [[i for i, curr_input_token in enumerate(curr_input_tokens) if len(curr_input_token) == 1] for
                       curr_input_tokens in input_tokens]
    letters_segments = [
        [(curr_new_letters_idx[i], curr_new_letters_idx[i + 1] - 1) for i in range(len(curr_new_letters_idx) - 1)] for
        curr_new_letters_idx in new_letters_idx]
    error_dist = [
        [[int(true_labels[i][j] != true_predictions[i][j]) for j in range(letter_segment[0], letter_segment[1] + 1)] for
         letter_segment in curr_letters_segments] for i, curr_letters_segments in enumerate(letters_segments)]
    flatten_dist = [item for row in error_dist for item in row]
    edr = sum([sum(word)/len(word) for word in flatten_dist]) / len(flatten_dist)
    print("EDR = ", edr)

    trios = [
        [(id_to_label[p][-1], id_to_label[l][-1], tokenizer.decode(i)[-1]) for (p, l, i) in
         zip(prediction, label, inputs) if l != -100]
        for prediction, label, inputs in zip(predictions, labels, inputs)
    ]
    flatten_trios = []
    for trio_list in trios:
        flatten_trios.extend(trio_list)

    confusion_mat_ar_ar = {l_expected[-1]: {l_result[-1]: 0 for l_result in label_to_id.keys()} for l_expected in
                           label_to_id.keys()}
    for (p, l, i) in flatten_trios:
        confusion_mat_ar_ar[l][p] += 1

    all_ja_letters = list(set([i for (p, l, i) in flatten_trios]))
    all_ja_letters.sort()

    mat_ja_ar_true = {l_from_ja[-1]: {l_to_ar[-1]: 0 for l_to_ar in label_to_id.keys()} for l_from_ja in
                      all_ja_letters}
    for (p, l, i) in flatten_trios:
        mat_ja_ar_true[i][l] += 1

    mat_ja_ar_pred = {l_from_ja[-1]: {l_to_ar[-1]: 0 for l_to_ar in label_to_id.keys()} for l_from_ja in
                      all_ja_letters}
    for (p, l, i) in flatten_trios:
        mat_ja_ar_pred[i][p] += 1

    print("confusion_mat_ar_ar")
    print(pd.DataFrame.from_dict(confusion_mat_ar_ar).to_latex())
    print()

    print("mat_ja_ar_true")
    print(pd.DataFrame.from_dict(mat_ja_ar_true).to_latex())
    print()

    print("mat_ja_ar_pred")
    print(pd.DataFrame.from_dict(mat_ja_ar_pred).to_latex())
    print()

    rare_trios = []
    for (p, l, i) in flatten_trios:
        if p in RARE_LETTERS or l in RARE_LETTERS:
            rare_trios.append((p, l))

    rare_true, rate_pred = [l for (p, l) in rare_trios], [p for (p, l) in rare_trios]
    print("precision_score macro: ", sklearn.metrics.precision_score(rare_true, rate_pred, average='macro'))
    print("precision_score micro: ", sklearn.metrics.precision_score(rare_true, rate_pred, average='micro'))
    print("recall_score macro: ", sklearn.metrics.recall_score(rare_true, rate_pred, average='macro'))
    print("recall_score micro: ", sklearn.metrics.recall_score(rare_true, rate_pred, average='micro'))
    print("f1_score macro: ", sklearn.metrics.f1_score(rare_true, rate_pred, average='macro'))
    print("f1_score micro: ", sklearn.metrics.f1_score(rare_true, rate_pred, average='micro'))
    print("accuracy: ", sklearn.metrics.accuracy_score(rare_true, rate_pred))
    print("size rare = ", len(rare_trios))

    all_true, all_pred = [l for (p, l, i) in flatten_trios], [p for (p, l, i) in flatten_trios]
    print("all precision_score macro: ", sklearn.metrics.precision_score(all_true, all_pred, average='macro'))
    print("all precision_score micro: ", sklearn.metrics.precision_score(all_true, all_pred, average='micro'))
    print("all recall_score macro: ", sklearn.metrics.recall_score(all_true, all_pred, average='macro'))
    print("all recall_score micro: ", sklearn.metrics.recall_score(all_true, all_pred, average='micro'))
    print("all f1_score macro: ", sklearn.metrics.f1_score(all_true, all_pred, average='macro'))
    print("all f1_score micro: ", sklearn.metrics.f1_score(all_true, all_pred, average='micro'))
    print("all accuracy: ", sklearn.metrics.accuracy_score(all_true, all_pred))
    print("all size rare = ", len(flatten_trios))

    results = metric.compute(predictions=true_predictions, references=true_labels)
    print(results)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }


def print_stats(x):
    c = get_all_couples(x)
    print(x)
    print("words = ", len(c))
    print("letters = ", sum([len(subc) for subc in c]))


print_stats("tahafutalfalsafa")
print_stats("tahafutaltahafut")
print_stats("hakdamalamishna")
print_stats("imanat")
print_stats("alkuzari")

couples_train = get_all_couples("tahafutalfalsafa") + get_all_couples("tahafutaltahafutt") + get_all_couples("hakdamalamishna") + get_all_couples("imanat")
couples_test = get_all_couples("alkuzari")

words_train = make_words_list(couples_train, keep_apostrophe=False)
words_test = make_words_list(couples_test, keep_apostrophe=False)

gs_train = split_into_subgroups(words_train, g_size=100)
gs_test = split_into_subgroups(words_test, g_size=100)

tokenized_train_ds = make_tokenized_datasets(gs_train, should_split=False)
tokenized_test_ds = make_tokenized_datasets(gs_test, should_split=False)

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    num_train_epochs=10,
    weight_decay=0.01,
    overwrite_output_dir=True,
    optim="adamw_torch",
    logging_steps=1000000,
    load_best_model_at_end=False,
    save_total_limit=2,
    save_strategy="no",
    hub_model_id="dwmit/transliterate_try",
    hub_token="",  # CREDENTIALS
    push_to_hub=False,
    include_inputs_for_metrics=True,
)

metric = evaluate.load("seqeval")
model = AutoModelForTokenClassification.from_pretrained("dwmit/transliterate", num_labels=34, ignore_mismatched_sizes=True, id2label=id_to_label, label2id=label_to_id)
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_ds,
    eval_dataset=tokenized_test_ds,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer,
    data_collator=data_collator
)

print("Started training")
trainer.train()
print("Started evaluation")
trainer.evaluate()
print("train size = ", len(tokenized_train_ds))
print("test size = ", len(tokenized_test_ds))
print("train size (by row) = ", sum([len(row) for row in tokenized_train_ds]))
print("test size (by row) = ", sum([len(row) for row in tokenized_test_ds]))

# trainer.save_model("./transliterate-try-trained")
