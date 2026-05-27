import os
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Dynamic project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, 'local_models', 'weights', 'all-MiniLM-L6-v2')

model = SentenceTransformer(model_path)

@app.route('/encode', methods=['POST'])
def encode():
    data = request.json
    emb = model.encode(data['text'])
    return jsonify({'embedding': emb.tolist()})

if __name__ == '__main__':
    app.run(port=5001)
