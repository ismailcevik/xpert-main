
from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'gizli-anahtar'

from modules import limitler, raporlama, sistemfan, zamanlar, sistemfantrend, geneldurum, scada
app.register_blueprint(limitler.bp)
app.register_blueprint(raporlama.bp)
app.register_blueprint(sistemfan.bp)
app.register_blueprint(zamanlar.bp)
app.register_blueprint(sistemfantrend.bp)
app.register_blueprint(geneldurum.bp)
app.register_blueprint(scada.bp)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in ['ismailcevik', 'gulsahcevik'] and password == '12345':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Kullanıcı adı veya şifre hatalı!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
