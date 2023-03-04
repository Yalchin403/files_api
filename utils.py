import openai
import random
import string
import re
from string import punctuation
from flask import jsonify
from nltk.tokenize import word_tokenize
from transformers import pipeline


api_key = "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"
openai.api_key = api_key

model = pipeline('summarization')


def generate_random_key():
  return ''.join(random.sample(string.ascii_letters + string.digits, 16))


def transformer_summary(text):
  tokens = 500
  word_count = int(tokens*0.75)
      
  useful_text = "References".join(text.split("References")[:-1])
  words = word_tokenize(useful_text)
  summary_text = useful_text

  while len(words) > 2000:
    chunks = []
    for count in range(0, len(words), word_count):
      chunks.append(' '.join(words[count: count+word_count]))

      result = model(chunks, max_length=1024, min_length=5, num_beams=3, do_sample=False)

      summary_text = ' '.join([r['summary_text'].strip() for r in result])
      words = word_tokenize(summary_text)
      
  return summary_text


def generate_keywords(text, model):
  try:
    response = openai.Completion.create(
      model=model,
      prompt=
      f"""Generate 10 keywords separated by comma which are good for seo from the following content:{text}\n10 Keywords separated by comma:""",
      temperature=0.6,
      max_tokens=250)
  except openai.error.ServiceUnavailableError:
    resp = jsonify({"message": "OpenAI service overloaded"})
    resp.status_code = 400
    return resp

  content = response['choices'][0]['text']
  content = content.split(',')
  keywords = [f"{num}. {keyword.strip()}" for num, keyword in enumerate(content, 1)]
  content = "\n".join(keywords)
  
  token_num = response['usage']['total_tokens']
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
      max_tokens=750)
  except openai.error.ServiceUnavailableError:
    resp = jsonify({"message": "OpenAI service overloaded"})
    resp.status_code = 400
    return resp

  content = response['choices'][0]["text"].strip()
  token_num = response['usage']['total_tokens']
  return content, token_num


def generate_titles(text, model):
  try:
    response = openai.Completion.create(
      model=model,
      prompt=
      f"Generate ten long informative titles separated by ~ from the following paragraph: {text}\n10 Titles separated by ~:",
      temperature=0.8,
      max_tokens=350)
    
  except openai.error.ServiceUnavailableError:
    resp = jsonify({"message": "OpenAI service overloaded"})
    resp.status_code = 400
    return resp

  content = response['choices'][0]['text']
  content = content.replace('"', '')
  content = content.split('~')

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
  
  token_num = response['usage']['total_tokens']
  return content, token_num