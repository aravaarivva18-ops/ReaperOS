import os
import time
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from knowledge_brain import add_telemetry, get_process_status, get_latest_telemetry

app = Flask(__name__)

# Динамический корень проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, 'local_models', 'weights', 'all-MiniLM-L6-v2')

# Ленивая загрузка модели для тестов (если веса еще не скачаны)
model = None

def get_model():
    global model
    if model is None:
        if os.path.exists(model_path):
            model = SentenceTransformer(model_path)
        else:
            # Фолбек на скачивание (или заглушка для тестов)
            model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

@app.after_request
def add_cors_headers(response):
    """Добавление заголовков CORS вручную без внешних библиотек."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'time': time.time()})

@app.route('/encode', methods=['POST'])
def encode():
    start_time = time.time()
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400
        
    try:
        m = get_model()
        emb = m.encode(data['text'])
        latency_ms = (time.time() - start_time) * 1000
        
        # Пишем телеметрию
        add_telemetry("encode_latency", latency_ms, f"Text length: {len(data['text'])}")
        
        # SLI предупреждение в логи при задержке >500ms
        if latency_ms > 500:
            print(f"⚠️ [WARNING] SLI Breach: encode_latency = {latency_ms:.1f}ms (>500ms)")
            add_telemetry("sli_warning", latency_ms, "encode_latency > 500ms")
            
        return jsonify({'embedding': emb.tolist(), 'latency_ms': latency_ms})
    except Exception as e:
        add_telemetry("encode_error", 1.0, str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Эндпоинт для Bento Dashboard: статус процессов."""
    try:
        status_data = get_process_status()
        return jsonify({'status': 'success', 'data': status_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/telemetry', methods=['GET'])
def api_telemetry():
    """Эндпоинт для Bento Dashboard: последние метрики задержки."""
    try:
        metric_name = request.args.get('metric', 'encode_latency')
        telemetry_data = get_latest_telemetry(metric_name=metric_name, limit=20)
        return jsonify({'status': 'success', 'data': telemetry_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Сервер будет слушать на порту 5001
    app.run(host='127.0.0.1', port=5001)
