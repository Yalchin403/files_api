import openai
import random
import string

# import spacy
import re
import os

# from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from flask import jsonify
from nltk.tokenize import word_tokenize
from transformers import pipeline
import subprocess
import textract
from PyPDF2 import PdfReader


api_key = "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"
openai.api_key = api_key

model = pipeline("summarization")

valid_extensions = ["docx", "txt", "pdf", "odt", "doc"]


def check_extention(name):
    return name.split(".")[-1] in valid_extensions


def unsupported_filetype_response():
    print("File does not have supported extension type.")
    resp = jsonify(
        f"File does not have supported extension type. Supported extensions type are {', '.join(valid_extensions)}"
    )
    resp.status_code = 400
    return resp


def get_file_content(file):
    ext = file.filename.split(".")[-1].lower()
    if ext == "txt":
        content = file.read()
        return content.decode("utf-8")

    if ext == "pdf":
        f_name = os.path.join("uploads", os.path.basename(file.filename))
        file.save(f_name)

        content = []
        reader = PdfReader(f_name)
        for page in reader.pages:
            content.append(page.extract_text())
        os.remove(f_name)
        return "\n".join(content)

    if ext == "docx" or ext == "odt":
        f_name = os.path.join("uploads", os.path.basename(file.filename))
        file.save(f_name)
        text = textract.process(f_name)
        text = text.decode("utf-8")
        os.remove(f_name)
        return text

    if ext == "doc":
        f_name = os.path.join("uploads", file.filename)
        file.save(f_name)
        result = subprocess.run(["antiword", f_name], stdout=subprocess.PIPE)
        text = result.stdout.decode("utf-8")
        return text


def generate_random_key():
    return "".join(random.sample(string.ascii_letters + string.digits, 16))


# def summarize_content(text):
#   num_words = 2000 * 0.75
#   nlp = spacy.load('en_core_web_sm')
#   doc= nlp(text)
#   word_frequencies={}
#   for word in doc:
#     if word.text.lower() not in list(STOP_WORDS):
#       if word.text.lower() not in punctuation:
#         if word.text not in word_frequencies.keys():
#           word_frequencies[word.text] = 1
#         else:
#           word_frequencies[word.text] += 1
#   max_frequency=max(word_frequencies.values())
#   for word in word_frequencies.keys():
#     word_frequencies[word]=word_frequencies[word]/max_frequency
#   sentence_tokens= [sent for sent in doc.sents]
#   sentence_scores = {}
#   for sent in sentence_tokens:
#     for word in sent:
#       if word.text.lower() in word_frequencies.keys():
#         if sent not in sentence_scores.keys():
#           sentence_scores[sent]=word_frequencies[word.text.lower()]
#         else:
#           sentence_scores[sent]+=word_frequencies[word.text.lower()]

#   sentence_list = [(key, value) for key, value in sentence_scores.items()]
#   sorted_sentences = sorted(sentence_list, key=lambda x:x[1], reverse=True)

#   word_count = 0
#   final_summary = []
#   for sentence, _ in sorted_sentences:
#     sentence = str(sentence).strip()
#     count = len(word_tokenize(sentence))
#     if word_count + count < num_words:
#       final_summary.append(sentence)
#       word_count += count
#   return ''.join(final_summary)


def transformer_summary(text):
    tokens = 500
    word_count = int(tokens * 0.75)

    useful_text = "References".join(text.split("References")[:-1])
    words = word_tokenize(useful_text)
    summary_text = useful_text

    while len(words) > 2000:
        chunks = []
        for count in range(0, len(words), word_count):
            chunks.append(" ".join(words[count : count + word_count]))

            result = model(
                chunks, max_length=1024, min_length=5, num_beams=3, do_sample=False
            )

            summary_text = " ".join([r["summary_text"].strip() for r in result])
            words = word_tokenize(summary_text)

    return summary_text


def generate_keywords(text, model):
    try:
        response = openai.Completion.create(
            model=model,
            prompt=f"""Generate 10 keywords separated by comma which are good for seo from the following content:{text}\n10 Keywords separated by comma:""",
            temperature=0.6,
            max_tokens=250,
        )
    except openai.error.ServiceUnavailableError:
        resp = jsonify({"message": "OpenAI service overloaded"})
        resp.status_code = 400
        return resp

    content = response["choices"][0]["text"]
    content = content.split(",")
    keywords = [f"{num}. {keyword.strip()}" for num, keyword in enumerate(content, 1)]
    content = "\n".join(keywords)

    token_num = response["usage"]["total_tokens"]
    return content, token_num


def generate_abstract(text, model):
    prompt = f"""Write introduction, objective, methods, results in around 50 words each from the following paragraph. {text}\n
  Introduction: in around 100 words\n
  Objective: in 50 words\n
  Methods: in 50 words\n
  Results: in 30 words\n"""
    try:
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=0.7,
            presence_penalty=1,
            max_tokens=750,
        )
    except openai.error.ServiceUnavailableError:
        resp = jsonify({"message": "OpenAI service overloaded"})
        resp.status_code = 400
        return resp

    content = response["choices"][0]["text"].strip()
    token_num = response["usage"]["total_tokens"]
    return content, token_num


def generate_titles(text, model):
    try:
        response = openai.Completion.create(
            model=model,
            prompt=f"Generate ten long informative titles separated by ~ from the following paragraph: {text}\n10 Titles separated by ~:",
            temperature=0.8,
            max_tokens=350,
        )

    except openai.error.ServiceUnavailableError:
        resp = jsonify({"message": "OpenAI service overloaded"})
        resp.status_code = 400
        return resp

    content = response["choices"][0]["text"]
    content = content.replace('"', "")
    content = content.split("~")

    clean_content = []
    for line in content:
        line = line.strip()
        if line == "":
            continue
        # s = re.sub("^[({\[]", "", line)  # Removing starting brackets
        # s = re.sub("^[\d]*", "", s)  # Removing numbering
        # s = re.sub("^[.)}\]]", "", s)  # Removing cloasing brackets
        clean_content.append(line)

    #   titles = [f"{num}. {title.strip()}" for num, title in enumerate(content, 1)]
    content = "\n".join(clean_content)

    token_num = response["usage"]["total_tokens"]
    return content, token_num
