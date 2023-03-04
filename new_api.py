from flask import Flask, request, jsonify
import os
import subprocess
import textract
from PyPDF2 import PdfReader
import werkzeug
import nltk
from nltk.tokenize import word_tokenize
from utils import *
from tasks import process_user_request
from worker import celery

nltk.download('punkt')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SUMMARY_FOLDER'] = 'summarized/'
app.config["CELERY_BROKER_URL"] = "redis://redis:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://redis:6379/0"
app.debug = True
app.config["FLASK_DEBUG"] = 1

celery.conf.update(app.config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SUMMARY_FOLDER'], exist_ok=True)

model_dict = {
    'davinci': 'text-davinci-003',
    'curie': 'text-curie-001',
    'babbage': 'text-babbage-001',
    'ada': 'text-ada-001',
}


@app.route('/tokens', methods=['POST'])
def num_tokens():
  file = request.files['file']

  ext_flag = check_extention(file.filename)
  if not ext_flag:
    return unsupported_filetype_response()
  
  full_content = get_file_content(file)
  total_tokens = len(word_tokenize(full_content))*(4/3)
  resp = jsonify({'tokens': total_tokens})
  resp.status_code = 200
  return resp

  
@app.route('/', methods=['POST'])
def main():
  try:
      file = request.files['file']
  except werkzeug.exceptions.BadRequestKeyError:
    resp = jsonify({"message": "The browser (or proxy) sent a request that this server could not understand. KeyError: 'file'"})
    resp.status_code = 400
    return resp
  
  arg_model = request.form.get('model', 'davinci')
  model = model_dict[arg_model]
  
  # process_user_request.delay(file, model)
  # process_user_request.delay(1, 2)

  resp = jsonify({"message": "Process queued"})
  resp.status_code = 200
  return resp


@app.route('/regenerate', methods=['POST'])
def regenerate():
  key = request.form.get("key")
  task = request.form.get("task")
  arg_model = request.form.get("model", 'davinci')
  model = model_dict[arg_model]

  with open(f'{app.config["SUMMARY_FOLDER"]}/{key}.txt', 'rb') as f:
    final_text = f.read().decode('utf-8')

  if task == "abstract":
    content, token_used = generate_abstract(final_text, model)
  elif task == "keywords":
    content, token_used = generate_keywords(final_text, model)
  elif task == "title":
    content, token_used = generate_titles(final_text, model)
  else:
    print("The task is not properly defined. Available tasks are abstract, keywords, titles.")
    resp = jsonify("The task is not properly defined. Available tasks are abstract, keywords, titles.")
    resp.status_code = 400
    return resp

  resp = jsonify({"content": content, 'token_used': token_used})
  resp.status_code = 200
  return resp


if __name__ == '__main__':
  app.run()
