from flask import Blueprint, render_template, request, jsonify
from modules.utils import login_required
import json
import os

bp = Blueprint('geneldurum', __name__, url_prefix='/geneldurum')

DATA_FILE = 'geneldurum.json'

# Veriyi yükle
def load_status_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Veriyi kaydet
def save_status_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def panel():
    if request.method == 'POST':
        # Form verisini JSON dosyasına yaz
        new_data = request.get_json()
        save_status_data(new_data)
        return jsonify({'success': True})

    data = load_status_data()
    return render_template('geneldurum.html', data=data)
