from flask import Blueprint, render_template, request
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
    alarms = []
    trend_html = ''
    bar_chart_js = ''

    # Default değerler:
    selected_columns = []
    start_dt = None
    end_dt = None
    data = pd.DataFrame()

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        start_str = request.form.get('start_datetime')
        end_str = request.form.get('end_datetime')
        name = request.form.get('criteria_name')
        load_name = request.form.get('load_criteria')
        show_trend = 'show_trend' in request.form
        show_bar = True

        # Kriter yükleme varsa
        if load_name:
            crit = json.load(open(f"{KRITER_DIR}/{load_name}.json", encoding='utf-8'))
            selected_columns = crit['columns']
            start_dt = pd.to_datetime(crit['start'])
            end_dt = pd.to_datetime(crit['end'])
        else:
            # Kriter yüklenmediyse formdan al
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

            data = df[['RealDate'] + selected_columns]

            # Alarm tespiti
            for col in selected_columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    q1, q3 = df[col].quantile([0.25, 0.75])
                    iqr = q3 - q1
                    lim_low, lim_high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                    out = df[(df[col] < lim_low) | (df[col] > lim_high)]
                    for _, row in out.iterrows():
                        alarms.append({'tarih': row['RealDate'].strftime('%Y-%m-%d %H:%M'),
                                       'kolon': col, 'deger': row[col]})

            # Trend grafiği
            if show_trend and not data.empty:
                traces = [go.Scatter(x=data['RealDate'], y=data[c], mode='lines+markers', name=c) for c in selected_columns]
                fig = go.Figure(traces, layout=go.Layout(title='Trend Grafiği', xaxis_title='RealDate'))
                trend_html = pyo.plot(fig, output_type='div', include_plotlyjs=False)

            # Günlük ortalama bar grafiği
            if show_bar and not data.empty:
                df['date'] = df['RealDate'].dt.date
                grp = df.groupby('date')[selected_columns].mean().reset_index()
                labels = [str(d) for d in grp['date']]
                datasets = [{'label': c, 'data': [round(v, 2) for v in grp[c]]} for c in selected_columns]
                bar_chart_js = json.dumps({'labels': labels, 'datasets': datasets})

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
                           alarms=alarms,
                           trend_html=trend_html,
                           bar_chart_js=bar_chart_js,
                           start_dt_str=start_dt_str,
                           end_dt_str=end_dt_str)
