import os
import io
import base64
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import torch
from api import AnyCoastAPI

app = Flask(__name__)
CORS(app)

# Thư mục lưu trữ
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
LATENT_FOLDER = 'latents'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(LATENT_FOLDER, exist_ok=True)

# Khởi tạo API
device = 'cuda' if torch.cuda.is_available() else 'cpu'
api = AnyCoastAPI(device=device)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/directions', methods=['GET'])
def get_directions():
    directions = api.get_available_directions()
    return jsonify({'directions': directions})

@app.route('/encode', methods=['POST'])
def encode_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.jpg")
    file.save(file_path)
    
    try:
        # Encode ảnh
        latent_code = api.encode_image(file_path)
        
        # Lưu latent code
        latent_path = os.path.join(LATENT_FOLDER, f"{file_id}.pt")
        torch.save(latent_code, latent_path)
        
        # Tạo hình ảnh gốc
        img = api.generate_from_latent(latent_code)
        result_path = os.path.join(RESULT_FOLDER, f"{file_id}.jpg")
        img.save(result_path)
        
        # Chuyển đổi hình ảnh thành base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'latent_id': file_id,
            'image': img_str
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edit', methods=['POST'])
def edit_image():
    data = request.json
    
    if 'latent_id' not in data or 'direction' not in data:
        return jsonify({'error': 'Missing parameters'}), 400
    
    latent_id = data['latent_id']
    direction = data['direction']
    strength = float(data.get('strength', 1.0))
    channel_ratio = float(data.get('channel_ratio', 1.0))
    target_res = int(data.get('resolution', 1024))
    
    latent_path = os.path.join(LATENT_FOLDER, f"{latent_id}.pt")
    if not os.path.exists(latent_path):
        return jsonify({'error': 'Latent code not found'}), 404
    
    try:
        # Tải latent code
        latent_code = torch.load(latent_path, map_location=device)
        
        # Chỉnh sửa latent code
        edited_latent = api.edit_image(latent_code, direction, strength)
        
        # Tạo hình ảnh mới
        edited_id = f"{latent_id}_{direction}_{strength}"
        edited_latent_path = os.path.join(LATENT_FOLDER, f"{edited_id}.pt")
        torch.save(edited_latent, edited_latent_path)
        
        img = api.generate_from_latent(edited_latent, channel_ratio, target_res)
        result_path = os.path.join(RESULT_FOLDER, f"{edited_id}.jpg")
        img.save(result_path)
        
        # Chuyển đổi hình ảnh thành base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'latent_id': edited_id,
            'image': img_str
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)