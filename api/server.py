import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as palm
# import prompts # until we find a way to resolve modules on vercel
import traceback
import logging

palm.configure(api_key=os.environ['PALM_API_KEY'])

app = Flask(__name__)
cors = CORS(app)

# Model(name='models/text-bison-001', base_model_id='', version='001', display_name='Text Bison', description='Model targeted for text generation.', input_token_limit=4000, output_token_limit=1024, supported_generation_methods=['generateText'], temperature=0.7, top_p=0.95, top_k=40)

defaults = {
  'model': 'models/text-bison-001',
  'temperature': 0.7,
  'candidate_count': 1,
  'top_k': 40,
  'top_p': 0.95,
  'max_output_tokens': 1024,
}

prompts = {
  "BOOK_SUMMARY":
  """Summarize the book {place_holder} in a clear and concise way.

The summary should be no more than 1,000 words.
The summary should be written in a formal style.
The summary should include the following information:
The main plot points of the book.
The characters in the book and their roles.
The themes of the book.
The author's message.
Examples of desired output format:

"The book {place_holder} is about a young woman who goes on a journey to find herself. Along the way, she meets a variety of characters who help her to learn and grow. The book explores the themes of self-discovery, friendship, and love."

"{place_holder} is a classic novel that tells the story of a family's struggle to survive during the Great Depression. The book is full of memorable characters and powerful imagery. It is a must-read for anyone interested in American history."

Leading words and phrases:

The book {place_holder} is about...
The main plot points of the book are...
The characters in the book include...
The themes of the book are...
The author's message is...

Avoid vague or imprecise language:

Do not use words like "good" or "bad" to describe the book. Instead, be specific about what you liked or disliked about the book.
Do not use phrases like "it was a great book" or "it was a terrible book." Instead, explain why you thought the book was great or terrible.
Provide guidance on what should be done instead:

Instead of saying "do not include spoilers," say "please summarize the book without giving away any spoilers."
Instead of saying "do not use your own opinions," say "please provide a neutral summary of the book.
"""
  "",
  "ROOT_WORD":
  """Give me the root word of the Sanskrit word {place_holder}, give multiple meanings, and break it into syllables.

This prompt can be used for any Sanskrit word. The word {place_holder} should be replaced with the Sanskrit word that you want to learn about. The prompt will then give you the root word of the Sanskrit word, multiple meanings, and break it into syllables.

For example, if you wanted to learn about the Sanskrit word पुरूरवस्, you would replace {place_holder} with पुरूरवस्. The prompt would then give you the root word पुरु, multiple meanings for पुरु, and break down पुरूरवस् into syllables.""",
  "STRENGTHS":
  """Given Strengths & MBriggs provide me prompt that would guide the person to get better! Provide Pros, Cons and Thinks to improve. Keep it bullet points. For: {place_holder}"""
}


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/booksummary')
def booksummary():
  return render_template('book.html')


@app.route('/chat', methods=['POST'])
def chat():
  try:
    input_msg = request.json['message']
    if 'type' in request.json:
      prompt_type = request.json['type']
      input_msg = prompts.get(
        prompt_type.upper()).format(place_holder=input_msg)
    if not input_msg:
      return jsonify({'error': 'Empty message'})
    try:
      response = palm.chat(messages=input_msg)
      if response.last:
        return jsonify({'response': response.last})
    except Exception as chat_exception:
      exception = chat_exception
      try:
        response = palm.generate_text(prompt=input_msg, **defaults)
        if response.result:
          return jsonify({'response': response.result})
      except Exception as gen_text_exception:
        exception = gen_text_exception
        return jsonify(
          {'response': f"Sorry, I am still learning...{str(exception)}"})
  except Exception as e:
    return jsonify({'error': str(e)})


if __name__ == '__main__':
  app.config['REQUEST_TIMEOUT'] = 300
  app.run(host="0.0.0.0")
