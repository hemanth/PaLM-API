import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as palm

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


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
  try:
    input_msg = request.json['message']
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
  app.run()
