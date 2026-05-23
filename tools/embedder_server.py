from flask import Flask, request, jsonify; from sentence_transformers import SentenceTransformer; import os; app = Flask(__name__); model = SentenceTransformer('/Users/rus/Projects/ReaperOS/local_models/weights/all-MiniLM-L6-v2'); @app.route('/encode', methods=['POST']) 
def encode(): data = request.json; emb = model.encode(data['text']); return jsonify({'embedding': emb.tolist()}); 
if __name__ == '__main__': app.run(port=5001)
