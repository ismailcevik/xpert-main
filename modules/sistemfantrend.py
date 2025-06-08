from flask import Blueprint, Flask, render_template, request, jsonify
import pandas as pd
from modules.utils import login_required

bp = Blueprint('sistemfantrend', __name__, url_prefix='/sistemfantrend')

# Giriş sayfası
@bp.route('/', methods=['GET', 'POST'])
@login_required
def trendler():
    return render_template("sistemfantrend.html")  # Doğrudan template çağrısı

# Grafik verilerini sağlayan API
@bp.route('/get_data', methods=['POST'])
@login_required
def get_data():
    try:
        df = pd.read_excel("database.xlsx")
        timeframe = int(request.json.get("timeframe", 100))

        df = df.tail(timeframe).reset_index(drop=True)

        response = {
            "FIRIN TONAJI": df.get("FIRIN TONAJI", pd.Series([0]*timeframe)).fillna(0).tolist(),
            "FIRIN DEVRI": df.get("FIRIN DEVRI", pd.Series([0]*timeframe)).fillna(0).tolist(),
            "SISTEM FAN DEVRI": df.get("SISTEM FAN DEVRI", pd.Series([0]*timeframe)).fillna(0).tolist(),
            "TORBALI FILTRE GIRIS SICAKLIGI": df.get("TORBALI FILTRE GIRIS SICAKLIGI", pd.Series([0]*timeframe)).fillna(0).tolist(),

        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})

# Eğer doğrudan bu dosya çalıştırılıyorsa, Flask uygulamasını başlat
if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(debug=True)
