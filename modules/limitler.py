from modules.utils import login_required
import json
from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint


bp = Blueprint('limitler', __name__, url_prefix='/limitler')

# JSON dosyasına veri kaydetme fonksiyonu
def save_limits_to_json(data):
    with open('limitler.json', 'w') as f:
        json.dump(data, f, indent=4)

# JSON dosyasından veri yükleme fonksiyonu
def load_limits_from_json():
    try:
        with open('limitler.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Limitler route
@bp.route('/', methods=['GET', 'POST'])
@login_required
def limitler():
    # JSON dosyasındaki mevcut verileri alalım
    existing_data = load_limits_from_json()

    if request.method == 'POST':
        # Formdan gelen verileri alalım
        data = {
            'bacaCO': {
                'altLimit': request.form['bacaCOAltLimit'],
                'ustLimit': request.form['bacaCOUstLimit'],
                'altHedef': request.form['bacaCOAltHedef'],
                'ustHedef': request.form['bacaCOUstHedef']
            },
            'bacaO2': {
                'altLimit': request.form['bacaO2AltLimit'],
                'ustLimit': request.form['bacaO2UstLimit'],
                'altHedef': request.form['bacaO2AltHedef'],
                'ustHedef': request.form['bacaO2UstHedef']
            },
            'firinKafaBasinci': {
                'altLimit': request.form['firinKafaBasinciAltLimit'],
                'ustLimit': request.form['firinKafaBasinciUstLimit'],
                'altHedef': request.form['firinKafaBasinciAltHedef'],
                'ustHedef': request.form['firinKafaBasinciUstHedef']
            },
            'firinKafaSicakligi': {
                'altLimit': request.form['firinKafaSicakligiAltLimit'],
                'ustLimit': request.form['firinKafaSicakligiUstLimit'],
                'altHedef': request.form['firinKafaSicakligiAltHedef'],
                'ustHedef': request.form['firinKafaSicakligiUstHedef']
            },
            'fe': {
                'altLimit': request.form['feAltLimit'],
                'ustLimit': request.form['feUstLimit'],
                'altHedef': request.form['feAltHedef'],
                'ustHedef': request.form['feUstHedef']
            },
            'loi': {
                'altLimit': request.form['loiAltLimit'],
                'ustLimit': request.form['loiUstLimit'],
                'altHedef': request.form['loiAltHedef'],
                'ustHedef': request.form['loiUstHedef']
            },
            'intikalSicakligi': {
                'altLimit': request.form['intikalSicakligiAltLimit'],
                'ustLimit': request.form['intikalSicakligiUstLimit'],
                'altHedef': request.form['intikalSicakligiAltHedef'],
                'ustHedef': request.form['intikalSicakligiUstHedef']
            },
            'torbaliFiltreGirisSicakligi': {
                'altLimit': request.form['torbaliFiltreGirisSicakligiAltLimit'],
                'ustLimit': request.form['torbaliFiltreGirisSicakligiUstLimit'],
                'altHedef': request.form['torbaliFiltreGirisSicakligiAltHedef'],
                'ustHedef': request.form['torbaliFiltreGirisSicakligiUstHedef'],
            },
            'torbaliFiltreGirisBasinci': {
                'altLimit': request.form['torbaliFiltreGirisBasinciAltLimit'],
                'ustLimit': request.form['torbaliFiltreGirisBasinciUstLimit'],
                'altHedef': request.form['torbaliFiltreGirisBasinciAltHedef'],
                'ustHedef': request.form['torbaliFiltreGirisBasinciUstHedef'],
            }
        }

        # Verileri JSON dosyasına kaydet
        save_limits_to_json(data)

        # Veriler kaydedildikten sonra kullanıcıyı yönlendir
        return redirect(url_for('limitler.index'))

    return render_template('limitler.html', data=existing_data)

