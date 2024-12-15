from flask import Flask, render_template, request, redirect, url_for, send_file
import qrcode
from io import BytesIO
import os
import json
import uuid  # For unique ID generation

app = Flask(__name__)

# Folders for storing data and images
QR_FOLDER = 'static/qrcodes'
PHOTO_FOLDER = 'static/photos'
DATA_FILE = 'data.json'

# Create necessary folders
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

# Load existing data
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Helper function to save data
def save_data(data):
    with open(DATA_FILE, 'r') as f:
        existing_data = json.load(f)
    existing_data.update(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(existing_data, f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '')
        address = request.form.get('address', '')
        emp_code = request.form.get('emp_code', '')
        mobile = request.form.get('mobile', '')
        photo = request.files.get('photo')

        # Generate a unique ID for this QR code
        unique_id = str(uuid.uuid4())

        # Save photo
        photo_filename = ''
        if photo and photo.filename != '':
            photo_filename = os.path.join(PHOTO_FOLDER, f"{unique_id}_{photo.filename}")
            photo.save(photo_filename)

        # Store data
        user_data = {
            unique_id: {
                "name": name,
                "address": address,
                "emp_code": emp_code,
                "mobile": mobile,
                "photo": photo_filename.replace("\\", "/") if photo_filename else ""
            }
        }
        save_data(user_data)

        # Replace 'https://abcd1234.ngrok.io' with the actual ngrok URL displayed
        ngrok_url = 'https://abcd1234.ngrok.io'
        display_url = f"{ngrok_url}/display/{unique_id}"
        qr = qrcode.make(display_url)
        qr_code_path = os.path.join(QR_FOLDER, f"{unique_id}.png")
        qr.save(qr_code_path)

        return render_template('index.html', qr_code=qr_code_path, display_url=display_url)

    return render_template('index.html', qr_code=None)

@app.route('/display/<unique_id>')
def display(unique_id):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    user_data = data.get(unique_id)
    if not user_data:
        return "QR Code data not found!", 404

    return render_template('display.html', data=user_data)

@app.route('/download/<unique_id>')
def download(unique_id):
    qr_code_path = os.path.join(QR_FOLDER, f"{unique_id}.png")
    if os.path.exists(qr_code_path):
        return send_file(qr_code_path, as_attachment=True)
    return "QR Code not found!", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
