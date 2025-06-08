from modules.utils import login_required
from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO
from flask import Blueprint

bp = Blueprint('raporlama', __name__, url_prefix='/raporlama')

@bp.route('/', methods=['GET'])
@login_required
def index():
    df = pd.read_excel('database.xlsx')  # Excel dosyasını oku
    columns = df.columns.tolist()        # Sütun adlarını al
    return render_template('raporlama.html', columns=columns)

@bp.route('/export', methods=['POST'])
@login_required
def export():
    selected_columns = request.form.getlist('columns')  # Seçilen sütunları al
    df = pd.read_excel('database.xlsx', usecols=selected_columns)  # Seçilen sütunlarla dataframe oluştur

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="secili_veriler.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

