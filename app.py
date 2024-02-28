import re
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class FormData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

def send_to_telegram_form1(name, email):
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    message = f'New submission from Form 1:\nName: {name}\nEmail: {email}'
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}')

def send_to_telegram_form2(name, email):
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    message = f'New submission from Form 2:\nName: {name}\nEmail: {email}'
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}')

email_pattern = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if not name or not email:
            return render_template('slide_1.html', error="Please fill out all fields.")
        if not re.match(email_pattern, email):
            return render_template('slide_1.html', error="Please provide a valid email address.")

        new_form_data = FormData(name=name, email=email)
        db.session.add(new_form_data)
        db.session.commit()

        send_to_telegram_form1(name, email)

        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('slide_1.html')

@app.route('/form2', methods=['GET', 'POST'])
def form2():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Basic validation
        if not name or not email:
            return render_template('slide_2.html', error="Please fill out all fields.")
        if not re.match(email_pattern, email):
            return render_template('slide_2.html', error="Please provide a valid email address.")

        new_form_data = FormData(name=name, email=email)
        db.session.add(new_form_data)
        db.session.commit()

        send_to_telegram_form2(name, email)

        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('slide_2.html')

@app.route('/statut')
def statut():
    return render_template('statut.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/example')
def example():
    return render_template('example.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
