import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as palm

palm.configure(api_key=os.environ['PALM_API_KEY'])

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    input_msg = request.json['message']
    if not input_msg:
        return jsonify({'error': 'Empty message'})

    response = palm.chat(messages=input_msg)
    
    if not response.last:
        response = palm.generate_text(prompt=input_msg, **defaults)
        if not response.result:
            return jsonify({'response': 'Sorry I am still learning...'})
        return jsonify({'response': response.result})
    else:
        return jsonify({'response': response.last})

if __name__ == '__main__':
    app.run()

