from flask import Blueprint, render_template, request, send_file
from modules.utils import login_required
import pandas as pd
from io import BytesIO
import json
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.offline as pyo
import os

bp = Blueprint('raporlama', __name__, url_prefix='/raporlama')

KRITER_DIR = 'kriterler'
os.makedirs(KRITER_DIR, exist_ok=True)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    df = pd.read_excel('database.xlsx')
    if 'RealDate' not in df.columns:
        return "Excel dosyasında 'RealDate' sütunu bulunamadı.", 400
    df['RealDate'] = pd.to_datetime(df['RealDate'])
    columns = [c for c in df.columns if c != 'RealDate']

    criteria_list = [f[:-5] for f in os.listdir(KRITER_DIR) if f.endswith('.json')]
    trend_html = ''

    # Default değerler:
    selected_columns = []
    start_dt = None
    end_dt = None
    data = pd.DataFrame()
    hourly_avg_data = pd.DataFrame()

    load_name = request.form.get('load_criteria') if request.method == 'POST' else None

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        start_str = request.form.get('start_datetime')
        end_str = request.form.get('end_datetime')
        name = request.form.get('criteria_name')
        load_name = request.form.get('load_criteria')
        show_trend = 'show_trend' in request.form

        # Kriter yükleme varsa
        if load_name:
            crit = json.load(open(f"{KRITER_DIR}/{load_name}.json", encoding='utf-8'))
            selected_columns = crit['columns']
            start_dt = pd.to_datetime(crit['start']) if crit['start'] else None
            end_dt = pd.to_datetime(crit['end']) if crit['end'] else None
        else:
            start_dt = pd.to_datetime(start_str) if start_str else None
            end_dt = pd.to_datetime(end_str) if end_str else None

        # Kriter kaydetme
        if name:
            with open(f"{KRITER_DIR}/{name}.json", 'w', encoding='utf-8') as f:
                json.dump({'columns':selected_columns,
                           'start':start_dt.isoformat() if start_dt else '',
                           'end':end_dt.isoformat() if end_dt else ''}, f, ensure_ascii=False)
            if name not in criteria_list:
                criteria_list.append(name)

        if start_dt and end_dt:
            # Zaman filtresi
            df = df[(df['RealDate'] >= start_dt) & (df['RealDate'] <= end_dt)]

            # Tarihe göre eskiden yeniye sırala
            df = df.sort_values('RealDate')

            # Seçili sütunlar ve RealDate
            data = df[['RealDate'] + selected_columns]

            # Saatlik ortalama hesaplama (örneğin 08:00-09:00 gibi)
            if not data.empty:
                df_hourly = df.copy()
                df_hourly['hour'] = df_hourly['RealDate'].dt.floor('H')  # Saat bazında yuvarla
                hourly_avg = df_hourly.groupby('hour')[selected_columns].mean().reset_index()
                hourly_avg_data = hourly_avg.rename(columns={'hour': 'Saatlik Ortalama'})

            # Trend grafiği: Her sütun için ayrı scatter
            if show_trend and not data.empty:
                fig = go.Figure()
                for col in selected_columns:
                    fig.add_trace(go.Scatter(
                        x=data['RealDate'], y=data[col], mode='lines+markers', name=col,
                        hovertemplate='%{y}<extra></extra>'
                    ))
                fig.update_layout(title='Trend Grafiği', xaxis_title='RealDate', yaxis_title='Değer')
                trend_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    # HTML datetime-local input formatına çevirme
    def to_input_format(dt):
        if not dt:
            return ''
        return dt.strftime('%Y-%m-%dT%H:%M')

    start_dt_str = to_input_format(start_dt)
    end_dt_str = to_input_format(end_dt)

    return render_template('raporlama.html',
                           columns=columns,
                           criteria_list=criteria_list,
                           selected_columns=selected_columns,
                           data=data.to_dict('records'),
                           trend_html=trend_html,
                           start_dt_str=start_dt_str,
                           end_dt_str=end_dt_str,
                           hourly_avg_data=hourly_avg_data.to_dict('records'))

@bp.route('/export', methods=['POST'])
@login_required
def export_excel():
    df = pd.read_excel('database.xlsx')
    if 'RealDate' not in df.columns:
        return "Excel dosyasında 'RealDate' sütunu bulunamadı.", 400
    df['RealDate'] = pd.to_datetime(df['RealDate'])

    selected_columns = request.form.getlist('columns')
    start_str = request.form.get('start_datetime')
    end_str = request.form.get('end_datetime')

    start_dt = pd.to_datetime(start_str) if start_str else None
    end_dt = pd.to_datetime(end_str) if end_str else None

    if start_dt and end_dt:
        df = df[(df['RealDate'] >= start_dt) & (df['RealDate'] <= end_dt)]
        df = df.sort_values('RealDate')
    else:
        df = df.sort_values('RealDate')

    if selected_columns:
        df = df[['RealDate'] + selected_columns]
    else:
        df = df[['RealDate']]

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    filename = f"Rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return send_file(output, download_name=filename, as_attachment=True)

