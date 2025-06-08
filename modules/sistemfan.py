
from flask import Blueprint, render_template, session, redirect, url_for
from flask_socketio import emit, Namespace
from modules.utils import login_required
import json
import pandas as pd

bp = Blueprint('sistemfan', __name__, url_prefix='/sistemfan')

def load_limits():
    try:
        with open('limitler.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_zamanlar():
    try:
        with open('zamanlar.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def read_excel():
    try:
        df = pd.read_excel('database.xlsx')
        if 'RealDate' in df.columns:
            df['RealDate'] = pd.to_datetime(df['RealDate'])
            df = df.sort_values(by='RealDate', ascending=False)
            return df
        return None
    except FileNotFoundError:
        return None

def get_sistemfan_anlik():
    df = read_excel()
    return df.iloc[0].get('SISTEM FAN DEVRI', 0.0) if df is not None else None

def get_torbalifiltregiris_sicakligi_anlik():
    df = read_excel()
    return df.iloc[0].get('TORBALI FILTRE GIRIS SICAKLIGI', 0.0) if df is not None else None

def get_torbalifiltregiris_basinci_anlik():
    df = read_excel()
    return df.iloc[0].get('TORBALI FILTRE GIRIS BASINCI', 0.0) if df is not None else None

def get_torbalifiltregiris_sicakligi_ortalama():
    df = read_excel()
    zamanlar = load_zamanlar()
    if df is not None and zamanlar:
        dongu = int(zamanlar.get("SistemFan", {}).get("donguzamani", 1))
        return round(df.head(dongu)['TORBALI FILTRE GIRIS SICAKLIGI'].mean(), 2)
    return None

def get_torbalifiltregiris_basinci_ortalama():
    df = read_excel()
    zamanlar = load_zamanlar()
    if df is not None and zamanlar:
        dongu = int(zamanlar.get("SistemFan", {}).get("donguzamani", 1))
        return round(df.head(dongu)['TORBALI FILTRE GIRIS BASINCI'].mean(), 2)
    return None

def torbalifiltregiris_sicakligi_durum_fuzzy():
    df = read_excel()
    limitler = load_limits()
    zamanlar = load_zamanlar()
    if df is None or not limitler or not zamanlar:
        return None
    dongu = int(zamanlar.get("SistemFan", {}).get("donguzamani", 1))
    ortalama = df.head(dongu)['TORBALI FILTRE GIRIS SICAKLIGI'].mean()
    alt_hedef = float(limitler.get("torbaliFiltreGirisSicakligi", {}).get("altHedef", 0))
    ust_hedef = float(limitler.get("torbaliFiltreGirisSicakligi", {}).get("ustHedef", 100))
    alt_skala = float(limitler.get("fuzzydurum", {}).get("alt", -5))
    ust_skala = float(limitler.get("fuzzydurum", {}).get("ust", 5))
    if ortalama < alt_hedef:
        return -5
    elif ortalama > ust_hedef:
        return 5
    else:
        durum = ((ortalama - alt_hedef) / (ust_hedef - alt_hedef)) * (ust_skala - alt_skala) + alt_skala
        return round(durum, 1)

def torbalifiltregiris_basinci_durum_fuzzy():
    df = read_excel()
    limitler = load_limits()
    zamanlar = load_zamanlar()
    if df is None or not limitler or not zamanlar:
        return None
    dongu = int(zamanlar.get("SistemFan", {}).get("donguzamani", 1))
    ortalama = df.head(dongu)['TORBALI FILTRE GIRIS BASINCI'].mean()
    alt_hedef = float(limitler.get("torbaliFiltreGirisBasinci", {}).get("altHedef", 0))
    ust_hedef = float(limitler.get("torbaliFiltreGirisBasinci", {}).get("ustHedef", 100))
    alt_skala = float(limitler.get("fuzzydurum", {}).get("alt", -5))
    ust_skala = float(limitler.get("fuzzydurum", {}).get("ust", 5))
    if ortalama < alt_hedef:
        return -5
    elif ortalama > ust_hedef:
        return 5
    else:
        durum = ((ortalama - alt_hedef) / (ust_hedef - alt_hedef)) * (ust_skala - alt_skala) + alt_skala
        return round(durum, 1)

class SistemFanNamespace(Namespace):
    def on_connect(self):
        print('SistemFan client bağlandı.')

    def on_disconnect(self):
        print('SistemFan client ayrıldı.')

    def on_get_data(self):
        data = {
            "sistemfandevri_anlikveri": get_sistemfan_anlik(),
            "torbalifiltregirissicakligi_anlikveri": get_torbalifiltregiris_sicakligi_anlik(),
            "torbalifiltregirisbasinci_anlikveri": get_torbalifiltregiris_basinci_anlik(),
            "torbalifiltregirissicakligi_ortalamaveri": get_torbalifiltregiris_sicakligi_ortalama(),
            "torbalifiltregirisbasinci_ortalamaveri": get_torbalifiltregiris_basinci_ortalama(),
            "torbalifiltregirissicakligi_durum": torbalifiltregiris_sicakligi_durum_fuzzy(),
            "torbalifiltregirisbasinci_durum": torbalifiltregiris_basinci_durum_fuzzy(),
            "torbalifiltregirissicakligi_degisim": "?",
            "torbalifiltregirisbasinci_degisim": "?"
        }
        emit('update_data', data)

@bp.route('/status')
@login_required
def sistemfan_status():
    sistemfandata = load_limits()
    return render_template(
        'sistemfan.html',
        sistemfandata=sistemfandata,
        torbalifiltregirissicakligi_anlikveri=get_torbalifiltregiris_sicakligi_anlik(),
        torbalifiltregirissicakligi_ortalamaveri=get_torbalifiltregiris_sicakligi_ortalama(),
        torbalifiltregirissicakligi_durum=torbalifiltregiris_sicakligi_durum_fuzzy(),
        torbalifiltregirissicakligi_degisim='?',
        torbalifiltregirisbasinci_anlikveri=get_torbalifiltregiris_basinci_anlik(),
        torbalifiltregirisbasinci_ortalamaveri=get_torbalifiltregiris_basinci_ortalama(),
        torbalifiltregirisbasinci_durum=torbalifiltregiris_basinci_durum_fuzzy(),
        torbalifiltregirisbasinci_degisim='?',
        sistemfandevri_anlikveri=get_sistemfan_anlik(),
        user=session['user']
    )
