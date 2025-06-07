#!/usr/bin/env python3
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f:
        return "No file", 400
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
    f.save(save_path)
    return "OK", 200

@app.route('/dashboard')
def dashboard():
    files = []
    for filename in sorted(os.listdir(app.config['UPLOAD_FOLDER'])):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        stat = os.stat(path)
        files.append({
            'name': filename,
            'size': stat.st_size,
            'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template('dashboard.html', files=files)

@app.route('/downloads/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/')
def index():
    # Redirect to dashboard for simplicity
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
