import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from processing import new2old, old2new
import cv2

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed_image')

SERVER_URL = "http://1.15.143.65:8000"

app = Flask(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/processed_image/<filename>')
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

@app.route('/image-process', methods=['POST'])
def process_image_route():
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        extension = os.path.splitext(file.filename)[1]
        unique_filename = str(uuid.uuid4()) + extension

        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_path = os.path.join(PROCESSED_FOLDER, unique_filename)

        file.save(input_path)
        type = request.form.get('type')
        if not type:
            os.remove(input_path)
            return jsonify({'error': 'No type specified'}), 400

        original_image = cv2.imread(input_path)
        if original_image is None:
            os.remove(input_path)
            return jsonify({'error': 'Invalid image file'}), 400

        try:
            if type == 'xtpzj':
                fanhuang = int(request.form.get('fanhuang'))
                tuise = int(request.form.get('tuise'))
                huahen = int(request.form.get('huahen'))
                gaosimohu = int(request.form.get('gaosimohu'))
                processed_image = new2old(original_image, fanhuang, tuise, huahen, gaosimohu)
            elif type == 'ltpfx':
                processed_image = old2new(original_image)
            else:
                message = f'Type "{type}" is not supported'
                return jsonify({'error': message}), 400

            cv2.imwrite(output_path, processed_image)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        os.remove(input_path)
        image_url = f"{SERVER_URL}/processed_image/{unique_filename}"
        return jsonify({'success': True, 'image_url': image_url})

    return jsonify({'error': 'An unknown error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)