from modules.utils import login_required
import json
from flask import Blueprint, request, redirect, url_for, render_template

bp = Blueprint('zamanlar', __name__, url_prefix='/zamanlar')

# JSON dosyasına veri kaydetme fonksiyonu
def save_zamanlar_to_json(data):
    with open('zamanlar.json', 'w') as f:
        json.dump(data, f, indent=4)

# JSON dosyasından veri yükleme fonksiyonu
def load_zamanlar_from_json():
    try:
        with open('zamanlar.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@bp.route('/', methods=['GET', 'POST'])
@login_required
def zamanlar():
    existing_data = load_zamanlar_from_json()

    if request.method == 'POST':
        data = {
            'SistemFan': {
                'donguzamani': request.form.get('SistemFanDonguZamani', '')
            },
            'IDFan': {
                'donguzamani': request.form.get('IDFanDonguZamani', '')
            },
            'APFan': {
                'donguzamani': request.form.get('APFanDonguZamani', '')
            },
            'SogutmaFan': {
                'donguzamani': request.form.get('SogutmaFanDonguZamani', '')
            },
            'FirinKafaKomuru': {
                'donguzamani': request.form.get('FirinKafaKomuruDonguZamani', '')
            },
            'HGGKomuru': {
                'donguzamani': request.form.get('HGGKomuruDonguZamani', '')
            },
            'FirinTonaji': {
                'donguzamani': request.form.get('FirinTonajiDonguZamani', '')
            },
            'FirinDevri': {
                'donguzamani': request.form.get('FirinDevriDonguZamani', '')
            }
        }
        save_zamanlar_to_json(data)
        return redirect(url_for('zamanlar.zamanlar'))

    return render_template('zamanlar.html', data=existing_data)
