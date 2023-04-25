from flask import Flask, request, jsonify
import logging
from modelscope.models import Model
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import os

app = Flask(__name__)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s [%(levelname)s] %(message)s', filename='error.log')

model_dir = os.environ.get('MODEL_DIR')
if not model_dir:
    model_dir = ''
pipeline = pipeline(task=Tasks.chat, model=model_dir + 'ZhipuAI/ChatGLM-6B')

def get_complete(text, history=[]):
    resp = {}
    try:
        inputs = {'text': text, 'history': history}
        result = pipeline(inputs)
    except Exception as e:
        logging.error(f'text: {text}', exc_info=True)
        resp['status'] = 500
        resp['reason'] = 'internal server error'
        return resp
    else:
        resp['status'] = 200
        resp['result'] = result
        return resp


@app.route('/complete', methods=['POST'])
def complete():
    resp = {}
    params = request.get_json()
    if 'text' not in params:
        resp['status'] = 400
        resp['reason'] = "'text' is required"
        return jsonify(resp)
    text = params['text']
    try:
        assert isinstance(text, str)
    except AssertionError:
        resp['status'] = 400
        resp['reason'] = "'text' type must be string"
        return jsonify(resp)
    if 'history' not in params:
        return jsonify(get_complete(text))
    history = params['history']
    try:
        assert isinstance(history, list)
    except AssertionError:
        resp['status'] = 400
        resp['reason'] = "'history' type must be list"
        return jsonify(resp)
    else:
        return jsonify(get_complete(text, history))

@app.route('/check')
def check():
    return 'success'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9485)
