from worker import celery
from utils import *


@celery.task
def process_user_request(file, model):
  ext_flag = check_extention(file.filename)
  if not ext_flag:
    return unsupported_filetype_response()  

  full_content = get_file_content(file)
  full_content = transformer_summary(full_content)
  full_content = full_content.replace("\n", ' ')
  
  key = generate_random_key()
  with open(f'summarized/{key}.txt', "wb") as f:
    f.write(full_content.encode('utf-8'))
  
  token_used = 0
  final_text = full_content

  keyword_respoense, token_num = generate_keywords(final_text, model)
  token_used += token_num

  abstract_response, token_num = generate_abstract(final_text, model)
  token_used += token_num

  title_response, token_num = generate_titles(final_text, model)
  token_used += token_num

  resp = jsonify({
    "keywords": keyword_respoense, 
    "abstract": abstract_response,
    "titles": title_response,
    "key": key,
    "token_used": token_used})
  
  print("Sucess")