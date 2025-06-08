from flask import Blueprint, render_template
from modules.utils import login_required
import json
import os

bp = Blueprint('scada', __name__, url_prefix='/scada')

DATA_FILE = 'scada_data.json'
SVG_FILE = 'static/Scada Ekranı.drawio.svg'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "sistem_fan": 65,
        "torbali_filtre_giris_sicakligi": 150
    }

def load_svg():
    if os.path.exists(SVG_FILE):
        with open(SVG_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "<svg><text x='10' y='20'>SVG Yüklenemedi</text></svg>"

@bp.route('/')
@login_required
def scada_view():
    data = load_data()
    svg_content = load_svg()
    return render_template("scada.html", data=data, svg_content=svg_content, user="admin")
